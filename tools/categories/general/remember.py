from pathlib import Path
from datetime import datetime

from langchain.tools import tool

MEMORY_FILE = Path("knowledge/IO/general_memory.md")


def _ensure_file():
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text("", encoding="utf-8")


@tool
def remember_note(text: str) -> str:
    """Salva permanentemente una nota o un'informazione importante condivisa
    dall'utente (es. preferenze, dati personali da ricordare nelle conversazioni
    future). Usa questo tool solo quando l'utente chiede esplicitamente di
    ricordare qualcosa."""
    _ensure_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with MEMORY_FILE.open("a", encoding="utf-8") as f:
        f.write(f"- [{timestamp}] {text.strip()}\n")
    return "Nota salvata in memoria permanente."


@tool
def recall_notes(query: str = "") -> str:
    """Recupera le note salvate in memoria permanente. Se 'query' è vuota
    restituisce tutte le note, altrimenti filtra quelle che la contengono."""
    _ensure_file()
    content = MEMORY_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return "Non ho ancora nessuna nota salvata."

    if not query:
        return content

    matches = [line for line in content.splitlines() if query.lower() in line.lower()]
    return "\n".join(matches) if matches else "Nessuna nota corrispondente trovata."