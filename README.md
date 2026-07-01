# AIAgent

Agente AI locale basato su **LangGraph + Ollama** con pipeline a nodi (`memory -> reasoner -> planner -> executor -> critic -> final`), memoria persistente e tool operativi (knowledge base, note, data/ora, calcoli, audio).

## Cosa fa

- Chatta in locale usando un modello Ollama (default: `llama3.1`).
- Decide automaticamente se rispondere direttamente o usare tool.
- Esegue piani multi-step con dipendenze e parallelismo tra step indipendenti.
- Valida i risultati con un nodo di critica e tenta re-plan automatico (fino a 2 tentativi).
- Salva memoria conversazionale e recupera contesto semantico da file locali.

## Architettura rapida

Il grafo e definito in `core/Agent.py`:

```text
memory -> reasoner -> (planner | final)
planner -> executor -> critic -> (planner | final)
final -> END
```

Nodi principali:

- `memory`: costruisce contesto short-term + retrieval long-term.
- `reasoner`: decide `requires_tools`.
- `planner`: crea piano tool-calling strutturato.
- `executor`: esegue tool con gestione dipendenze/parallelo.
- `critic`: valida output e decide eventuale retry.
- `final`: genera risposta finale in italiano usando solo dati osservati.

## Struttura progetto

```text
AIAgent/
  main.py
  core/
	Agent.py
	nodes/
  tools/
	tools.py
	categories/general/
  knowledge/
	bookshelf/
	IO/
  requirements.txt
```

## Prerequisiti

- Python 3.11+ (consigliato ambiente virtuale).
- Ollama installato e in esecuzione.
- Modello Ollama disponibile localmente (es. `llama3.1`).

Dipendenze audio usate dai tool ma non sempre presenti nel lock:

- `SpeechRecognition` (speech-to-text).
- `gTTS` (text-to-speech).
- opzionali: `pydub` + `ffmpeg` (conversione mp3 -> wav per trascrizione file).
- per input da microfono puo servire `PyAudio` (o backend equivalente).

## Installazione

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install SpeechRecognition gTTS pydub
```

Preparazione modello Ollama:

```powershell
ollama pull llama3.1
```

## Avvio

```powershell
python main.py
```

Comandi di uscita in chat: `exit`, `quit`, `q`.

## Tool disponibili

Registrati in `tools/tools.py`:

- `search_docs(query)`: ricerca semantica in `knowledge/bookshelf` e `knowledge/IO`.
- `remember_note(text)`: salva nota permanente in `knowledge/IO/general_memory.md`.
- `recall_notes(query)`: recupera note salvate.
- `get_current_datetime(timezone)`: data/ora locale.
- `calculator(expression)`: calcolatrice sicura via AST.
- `list_available_tools()`: elenco tool.
- `speak_text(text, play)`: sintesi vocale e salvataggio mp3.
- `transcribe_audio_file(audio_path)`: trascrizione da file audio.
- `listen_from_microphone(duration_seconds)`: trascrizione live da microfono.

## Memoria e knowledge

- Memoria conversazioni: `knowledge/IO/agent_memory.md`.
- Memoria esplicita (note): `knowledge/IO/general_memory.md`.
- Prompt di identita: `knowledge/IO/role.md`, `knowledge/IO/personality.md`.
- Base documentale personale: `knowledge/bookshelf/*` (`.txt`, `.md`).

Il retrieval usa FAISS + embeddings (`sentence-transformers/all-MiniLM-L6-v2`) con fallback keyword.

## Tracing opzionale (LangSmith)

Se imposti `LANGSMITH_API_KEY` (o `LANGCHAIN_API_KEY`), il tracing si attiva automaticamente (`setup_langsmith` in `core/Agent.py`).

## Note operative

- `main.py` istanzia `AgentInstance("llama3.1")`: cambia qui il modello di default se necessario.
- Il nodo `final` evita di inventare dati quando i tool non producono output utile.
- Ci sono file legacy/non centrali (es. `core/LLM.py`, `test.py`) non usati dal loop principale.

## Troubleshooting veloce

- **Errore Ollama/model not found**: verifica che Ollama sia attivo e fai `ollama pull <modello>`.
- **Tool audio non disponibili**: installa `SpeechRecognition`, `gTTS`, eventuale `PyAudio`, `pydub` e `ffmpeg`.
- **Knowledge base vuota**: aggiungi file in `knowledge/bookshelf` e riprova `search_docs`.
- **Risposte senza tool quando attesi**: riformula la richiesta in modo esplicito (es. "cerca nei file...", "calcola...", "ricorda...").
