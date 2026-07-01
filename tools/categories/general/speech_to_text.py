"""
Speech To Text
==============
Riconoscimento vocale in italiano via SpeechRecognition (Google Speech API,
gratuita, richiede rete). Due tool: trascrizione da file audio esistente e
ascolto dal microfono per N secondi.
"""

from pathlib import Path

from langchain.tools import tool

LANGUAGE = "it-IT"


def _get_recognizer():
    import speech_recognition as sr
    return sr, sr.Recognizer()


@tool
def transcribe_audio_file(audio_path: str) -> str:
    """Trascrive in testo italiano un file audio esistente (wav, aiff, flac;
    per mp3 serve ffmpeg installato). Usa questo tool quando l'utente
    fornisce un percorso a un file audio da trascrivere."""
    path = Path(audio_path)
    if not path.exists():
        return f"File audio non trovato: {audio_path}"

    try:
        sr, recognizer = _get_recognizer()
    except ImportError:
        return "Libreria 'SpeechRecognition' non installata. Esegui: pip install SpeechRecognition"

    source_path = path
    temp_wav = None

    if path.suffix.lower() not in (".wav", ".aiff", ".flac"):
        try:
            from pydub import AudioSegment
            import tempfile

            temp_wav = Path(tempfile.mktemp(suffix=".wav"))
            AudioSegment.from_file(path).export(temp_wav, format="wav")
            source_path = temp_wav
        except Exception as e:
            return (
                f"Formato '{path.suffix}' non supportato direttamente e la conversione "
                f"è fallita ({e}). Serve 'pydub' + ffmpeg installati, oppure fornisci un file .wav."
            )

    try:
        with sr.AudioFile(str(source_path)) as audio_source:
            audio_data = recognizer.record(audio_source)
        text = recognizer.recognize_google(audio_data, language=LANGUAGE)
        return text
    except sr.UnknownValueError:
        return "Audio non comprensibile: non sono riuscito a riconoscere il parlato."
    except sr.RequestError as e:
        return f"Errore nel servizio di riconoscimento vocale: {e}"
    except Exception as e:
        return f"Errore durante la trascrizione: {e}"
    finally:
        if temp_wav and temp_wav.exists():
            temp_wav.unlink(missing_ok=True)


@tool
def listen_from_microphone(duration_seconds: int = 5) -> str:
    """Ascolta dal microfono per un numero di secondi indicato e trascrive
    in testo italiano ciò che è stato detto. Usa questo tool solo quando
    l'utente chiede esplicitamente di 'ascoltare' o 'dettare' qualcosa."""
    try:
        sr, recognizer = _get_recognizer()
    except ImportError:
        return "Libreria 'SpeechRecognition' non installata. Esegui: pip install SpeechRecognition"

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.listen(source, timeout=duration_seconds, phrase_time_limit=duration_seconds)
        text = recognizer.recognize_google(audio_data, language=LANGUAGE)
        return text
    except sr.WaitTimeoutError:
        return "Nessun audio rilevato nel tempo previsto."
    except sr.UnknownValueError:
        return "Audio non comprensibile: non sono riuscito a riconoscere il parlato."
    except sr.RequestError as e:
        return f"Errore nel servizio di riconoscimento vocale: {e}"
    except OSError as e:
        return f"Microfono non disponibile: {e}"
    except Exception as e:
        return f"Errore durante l'ascolto: {e}"