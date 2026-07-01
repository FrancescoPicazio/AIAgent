from datetime import datetime

from langchain.tools import tool


@tool
def get_current_datetime(timezone: str = "") -> str:
    """Restituisce la data e l'ora correnti. Usa questo tool quando l'utente
    chiede che giorno/ora è, o per calcoli relativi a 'oggi', 'adesso', ecc.
    Il parametro timezone è opzionale e attualmente non utilizzato (ora locale)."""
    now = datetime.now()
    return now.strftime("%A %d %B %Y, ore %H:%M:%S")