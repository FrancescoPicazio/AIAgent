from typing import Any, Dict
from pydantic import BaseModel

from core.nodes.shared import AgentState, dump_model, json_dumps


class Critique(BaseModel):
    valid: bool = True
    issues: str = ""
    fix_suggestion: str = ""
    retry: bool = False


def _deterministic_critique(state: AgentState) -> Critique:
    plan = state.get("plan", {}) or {}
    result = state.get("result", {}) or {}
    steps = result.get("steps", {}) if isinstance(result, dict) else {}

    if plan.get("requires_tools") and not steps:
        return Critique(
            valid=False,
            issues="Il piano richiedeva tool ma non ci sono risultati.",
            fix_suggestion="Rigenera un piano con step validi.",
            retry=True,
        )

    errors = []
    for step_id, item in steps.items():
        if not item.get("ok", False):
            errors.append(f"{step_id}: {item.get('error', 'errore sconosciuto')}")

    if errors:
        return Critique(
            valid=False,
            issues="\n".join(errors),
            fix_suggestion="Correggi tool/argomenti o scegli un piano alternativo.",
            retry=True,
        )

    return Critique(valid=True, issues="", fix_suggestion="", retry=False)


def critic_node(agent_instance: Any, state: AgentState) -> Dict[str, Any]:
    deterministic = _deterministic_critique(state)
    if not deterministic.valid:
        critique = deterministic
    else:
        prompt = f"""
Sei il critic/observer di un agente ReAct.
Valuta se i risultati soddisfano la richiesta utente.
Non mostrare chain-of-thought: restituisci solo valid, issues, fix_suggestion, retry.

IMPORTANTE: un tool che restituisce un risultato vuoto o "nessun dato" (es. lista vuota,
0 risultati) NON è un fallimento. È un risultato valido e informativo. Non chiedere
retry solo perché il dato è vuoto: in quel caso valid=true, perché la risposta finale
puo' comunicare all'utente che non ci sono dati/operazioni disponibili.
retry=true SOLO se: il tool ha lanciato un errore (ok=False), oppure il piano ha
chiaramente usato lo strumento sbagliato per la richiesta.

Utente:
{agent_instance.get_latest_user_text(state)}

Piano:
{json_dumps(state.get("plan", {}))}

Risultati:
{json_dumps(state.get("result", {}))}

Regole:
- valid=false se un tool ha fallito o se manca un risultato necessario.
- retry=true solo se un nuovo piano puo correggere il problema.
- valid=true se la risposta finale puo essere prodotta.
"""
        critique = agent_instance.structured_invoke(Critique, prompt, fallback=deterministic)

    attempt = int(state.get("attempt", 0) or 0)
    critique.retry = bool(critique.retry and attempt < agent_instance.MAX_REPLAN)

    critique_dict = dump_model(critique)
    agent_instance.emit("CRITIQUE", critique_dict)

    update: Dict[str, Any] = {"critique": critique_dict}
    if critique.retry:
        update["attempt"] = attempt + 1
        agent_instance.emit("REPLAN", f"Tentativo {attempt + 1}/{agent_instance.MAX_REPLAN}")
    return update
