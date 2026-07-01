from langchain.tools import tool


@tool
def list_available_tools() -> str:
    """Mostra la lista dei tool disponibili e quando usarli."""
    return (
        "Tool disponibili:\n"
        "- search_docs(query): cerca nella knowledge base personale/RAG.\n"
        "- remember_note(text): salva una nota permanente solo su richiesta esplicita.\n"
        "- recall_notes(query): recupera note salvate in memoria permanente.\n"
        "- get_current_datetime(timezone): data e ora correnti.\n"
        "- calculator(expression): calcoli matematici sicuri.\n"
        "- speak_text(text, play): sintesi vocale in italiano.\n"
        "- transcribe_audio_file(audio_path): trascrizione audio da file.\n"
        "- listen_from_microphone(duration_seconds): ascolto microfono.\n"
    )
