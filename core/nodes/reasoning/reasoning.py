from typing import Any, Dict

from core.nodes.shared import AgentState
from core.nodes.reasoning.declination import ReasoningDecision


def _heuristic_decision( user_text: str) -> ReasoningDecision:
    low = user_text.lower()
    keywords = [
        "tool", "strument",
        "ora",
        "ore",
        "giorno",
        "data",
        "calcola",
        "quanto fa",
        "file",
        "knowledge",
        "document",
        "password",
        "parola d'ordine",
        "ricorda",
        "memoria",
        "nota",
        "audio",
        "microfono",
        "trascrivi",
        "leggi ad alta voce",
    ]
    requires = any(k in low for k in keywords)
    return ReasoningDecision(
        requires_tools=requires,
        task_summary=user_text[:180],
        reason="Heuristic routing.",
    )

def reasoner_node(agent_instance: "Any", state: AgentState) -> Dict[str, Any]:
    user_text = agent_instance.get_latest_user_text(state)

    prompt = f"""
    Sei il reasoner di un agente locale.
    Decidi se servono tool reali per rispondere. Non mostrare catena di pensiero.

    Tool disponibili:
    {agent_instance.tool_catalog}

    Richiesta utente:
    {user_text}

    Regole:
    - Se la richiesta riguarda file, knowledge base, memoria, data/ora,
      calcoli, voce/audio o lista tool, requires_tools=true.
    - Se e solo small talk o risposta generale, requires_tools=false.
    - Rispondi con uno schema strutturato compatibile con ReasoningDecision.
    """

    decision = agent_instance.structured_invoke(
        ReasoningDecision,
        prompt,
        fallback=_heuristic_decision(user_text),
    )

    # Override deterministico: se l'euristica rileva keyword forti che
    # implicano necessariamente un tool, non fidarti del solo giudizio LLM.
    heuristic = _heuristic_decision(user_text)
    if heuristic.requires_tools and not decision.requires_tools:
        decision = heuristic

    agent_instance.emit(
        "REASONER",
        {
            "requires_tools": decision.requires_tools,
            "summary": decision.task_summary,
            "reason": decision.reason,
        },
    )

    update = {
        "requires_tools": decision.requires_tools,
        "task_summary": decision.task_summary or user_text[:180],
    }
    if not decision.requires_tools:
        # pulisci stato residuo del turno precedente
        update["plan"] = {}
        update["result"] = {}
        update["critique"] = {}
    return update