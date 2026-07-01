"""
Text To Speech
==============
Sintesi vocale in italiano via gTTS (Google Text-to-Speech). Scelta di
design: gTTS richiede una breve chiamata di rete ma garantisce una voce
italiana naturale senza dover scaricare/gestire modelli neurali pesanti
in locale.
"""

import os
import platform
import subprocess
import tempfile
import uuid
from pathlib import Path

from langchain.tools import tool

OUTPUT_DIR = Path("knowledge/IO/tts_output")


def _play_audio(path: Path):
    """Riproduzione best-effort con il player di default del sistema.
    Se non riesce, non blocca: l'audio resta comunque salvato su disco."""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["afplay", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


@tool
def speak_text(text: str, play: bool = True) -> str:
    """Convertisce un testo in audio parlato in italiano e lo salva su file
    (riproducendolo automaticamente se 'play' è True). Usa questo tool
    quando l'utente chiede esplicitamente di 'leggere ad alta voce' o
    'dire' qualcosa, non per risposte testuali normali."""
    try:
        from gtts import gTTS
    except ImportError:
        return "Libreria 'gTTS' non installata. Esegui: pip install gTTS"

    if not text.strip():
        return "Nessun testo da sintetizzare."

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"tts_{uuid.uuid4().hex[:8]}.mp3"

    try:
        tts = gTTS(text=text.strip(), lang="it")
        tts.save(str(out_path))
    except Exception as e:
        return f"Errore durante la sintesi vocale: {e}"

    if play:
        _play_audio(out_path)

    return f"Audio generato e salvato in {out_path}" + (" (riproduzione avviata)" if play else "")