from typing import Any, Dict

from core.nodes.shared import AgentState


def memory_node(agent_instance: Any, state: AgentState) -> Dict[str, str]:
    user_text = agent_instance.get_latest_user_text(state)
    recent_messages = state.get("messages", [])[-8:]
    short = "\n".join(
        agent_instance.get_message_text(m)
        for m in recent_messages
        if agent_instance.get_message_text(m)
    )
    long = ""
    if len(user_text.split()) >= 3:
        long = agent_instance.long_memory.retrieve(user_text, k=5)
    memory = (
        "SHORT_TERM_CONTEXT:\n"
        f"{short or 'Nessun contesto recente.'}\n\n"
        "LONG_TERM_RETRIEVAL:\n"
        f"{long or 'Nessun ricordo rilevante trovato.'}"
    )
    if agent_instance.verbose:
        agent_instance.emit("MEMORY_DEBUG", memory)
    return {"memory": memory}