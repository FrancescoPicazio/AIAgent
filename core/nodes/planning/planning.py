import re
from typing import Any, Dict

from core.nodes.shared import AgentState, dump_model, json_dumps
from core.nodes.planning.paln import Plan


def _extract_expression(text: str) -> str:
    matches = re.findall(r"[0-9\.\+\-\*\/\%\(\)\s]+", text)
    expression = max(matches, key=len).strip() if matches else text
    return expression or text


def _fallback_plan(user_text: str) -> Plan:
    low = user_text.lower()
    steps = []

    def step(tool: str, args: Dict[str, Any], purpose: str) -> None:
        steps.append(
            {
                "id": f"step_{len(steps) + 1}",
                "tool": tool,
                "args": args,
                "depends_on": [],
                "purpose": purpose,
            }
        )

    if "tool" in low or "strument" in low:
        step("list_available_tools", {}, "Mostrare i tool disponibili.")
    elif any(k in low for k in ["wallet", "portafoglio", "saldo", "bilancio"]):
        step("wallet", {}, "Recuperare andamento/saldo del portafoglio.")
    elif any(k in low for k in ["ora", "ore", "giorno", "data", "oggi"]):
        step("get_current_datetime", {}, "Recuperare data e ora correnti.")
    elif any(k in low for k in ["calcola", "quanto fa"]):
        expression = _extract_expression(user_text)
        step("calculator", {"expression": expression}, "Eseguire il calcolo.")
    elif any(k in low for k in ["file", "knowledge", "document", "password", "parola d'ordine"]):
        step("search_docs", {"query": user_text}, "Cercare nella knowledge base.")
    elif "ricorda" in low:
        step("remember_note", {"text": user_text}, "Salvare una nota esplicita.")
    elif "memoria" in low or "nota" in low:
        step("recall_notes", {"query": user_text}, "Recuperare note salvate.")

    return Plan(
        requires_tools=bool(steps),
        strategy="Piano fallback deterministico basato sull'intento.",
        thought_tree=[
            "Risposta diretta se non servono dati esterni.",
            "Tool dedicato quando la richiesta tocca domini operativi.",
        ],
        steps=steps,
    )



def _sanitize_plan(agentInsance: Any, plan: Plan, user_text: str) -> Plan:
    if not plan.requires_tools or not plan.steps:
        fallback = _fallback_plan(user_text)
        if fallback.steps:
            return fallback
        return Plan(requires_tools=False, strategy="Risposta diretta.", steps=[])

    sanitized = []
    seen = set()
    for idx, step in enumerate(plan.steps, 1):
        data = dump_model(step)
        step_id = str(data.get("id") or f"step_{idx}")
        if step_id in seen:
            step_id = f"{step_id}_{idx}"
        seen.add(step_id)

        tool = data.get("tool")
        if tool not in agentInsance.tool_map:
            continue

        args = data.get("args") if isinstance(data.get("args"), dict) else {}
        deps = [
            dep for dep in (data.get("depends_on") or [])
            if isinstance(dep, str)
        ]
        sanitized.append(
            {
                "id": step_id,
                "tool": tool,
                "args": args,
                "depends_on": deps,
                "purpose": str(data.get("purpose") or ""),
            }
        )

    if not sanitized:
        return _fallback_plan(user_text)

    return Plan(
        requires_tools=True,
        strategy=plan.strategy,
        thought_tree=plan.thought_tree[:3],
        steps=sanitized,
        final_response_hint=plan.final_response_hint,
    )

def planner_node(agent_instance: Any, state: AgentState) -> Dict[str, Any]:
        user_text = agent_instance.get_latest_user_text(state)
        attempt = int(state.get("attempt", 0) or 0)

        if not state.get("requires_tools", False):
            plan = Plan(
                requires_tools=False,
                strategy="Risposta diretta senza tool.",
                steps=[],
            )
            plan_dict = dump_model(plan)
            agent_instance.emit("PLAN", plan_dict)
            return {"plan": plan_dict}

        prompt = f"""
Sei il planner di un agente LangGraph locale.
Crea un piano eseguibile, non una risposta finale.

Metodi da integrare:
- ReAct: pianifica azioni osservabili e poi valuta le osservazioni.
- Reflexion: se c'e una critica precedente, correggi il piano.
- Tree of Thoughts: fornisci solo alternative sintetiche, non ragionamento privato.
- Plan-and-execute: ogni step deve essere un tool reale.

Tool catalog con schema reale:
{agent_instance.tool_catalog}

Memoria/RAG:
{state.get("memory", "")}


Richiesta utente:
{user_text}

Tentativo: {attempt}
Critica precedente:
{json_dumps(state.get("critique", {}))}

Risultato precedente:
{json_dumps(state.get("result", {}))}

Regole rigide:
- Usa solo nomi tool presenti nel catalogo.
- Gli args devono rispettare lo schema del tool.
- Step indipendenti devono avere depends_on=[] per consentire parallelismo.
- Se l'utente chiede dati in file o knowledge base, usa search_docs.
- Se chiede lista tool, usa list_available_tools.
- Non inventare output dei tool.
"""
        fallback = _fallback_plan(user_text)
        plan = agent_instance.structured_invoke(Plan, prompt, fallback=fallback)
        plan = _sanitize_plan(agent_instance, plan, user_text)
        plan_dict = dump_model(plan)

        agent_instance.emit("PLAN", plan_dict)
        return {"plan": plan_dict}