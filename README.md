# AI Software Engineer Agent

Un **agente AI autonomo locale** che agisce come un software engineer senior di livello enterprise. Sistema basato su **LangGraph + Ollama + LangChain**, progettato per comprendere, progettare e modificare progetti software complessi con supervision umana continua.

---

## 🎯 Obiettivo

Costruire un ambiente di sviluppo dove l'utente possa interagire via chat naturale:

```
"Aggiungi autenticazione JWT al progetto"
```

E l'agente sia in grado di:

✅ **Comprendere il progetto** — analizzare requisiti, struttura, dipendenze  
✅ **Pianificare il lavoro** — decomporsi in task atomici ordinati  
✅ **Modificare il codice** — creare file, applicare patch, rispettare regole  
✅ **Validare i risultati** — test, lint, review, correzione automatica  
✅ **Mantenere memoria** — evoluzione della conoscenza del progetto nel tempo  
✅ **Mantenere controllo umano** — richiedere approvazione su decisioni critiche  

Non un semplice generatore di codice, ma un vero **sistema di ingegneria del software autonomo**.

---

## 🏗️ Principi fondamentali

### 1. **Human in the Loop** 👤

L'utente mantiene **sempre l'approvazione finale**.

**L'agente può autonomamente:**
- Analizzare requisiti e codebase
- Proporre soluzioni alternative
- Implementare modifiche già approvate
- Eseguire test e validazioni
- Suggerire miglioramenti

**L'agente NON può autonomamente:**
- Cambiare l'architettura principale
- Eliminare funzionalità
- Modificare elementi critici senza approvazione
- Effettuare merge definitivi senza conferma
- Fare scelte di design di alto livello

### 2. **Local First** 🔒

L'intero sistema funziona **100% localmente**.

```
✓ Nessun codice esce dalla macchina
✓ Nessuna dipendenza da API cloud
✓ Modelli LLM via Ollama locale
✓ Memoria e database locali (SQLite)
✓ Privacy completa e controllo totale
```

---

## 🛠️ Stack tecnologico

### LLM Runtime: **Ollama**

Responsabilità:
- Gestione modelli locali (Qwen3 4B, Qwen3-Coder, Gemma, DeepSeek)
- Inferenza locale con quantizzazione Q4/Q5
- Esposizione API REST per tool calling
- Ottimizzazione hardware AMD RX 6800 XT via ROCm

### Framework Agentico: **LangChain + LangGraph**

**LangChain** — gestione:
- Tool e tool calling
- Prompt engineering e template
- Retrieval-Augmented Generation (RAG)
- Integrazione modelli e memoria

**LangGraph** — orchestrazione principale:
- Definizione workflow e grafo degli agenti
- Gestione stato globale condiviso
- Transizioni tra nodi specializzati
- Loop di correzione automatica
- Checkpoint e recovery in crash

### Monitoring: **LangSmith**

- Tracciamento chiamate LLM e risposte
- Metriche di qualità degli agenti
- Individuazione errori e regressioni
- Benchmark e valutazione continua

---

## 🧠 Architettura: Agenti specializzati

### **Architect Agent**

Analizza requisiti e propone soluzioni architetturali.

**Output:**
- Documento di progettazione
- Piano tecnico dettagliato
- Valutazione rischi e impatti

---

### **Planner Agent**

Trasforma una richiesta in task atomici ordinati con dipendenze.

**Esempio input:**
```
"Aggiungi autenticazione JWT"
```

**Esempio output:**
```
TASK 1: Creare modello Utente
  - File: models/user.py
  - Funzioni: User class
  - Risk: LOW

TASK 2: Implementare repository Utenti
  - File: repositories/user_repo.py
  - Dipendenze: Task 1
  - Risk: LOW

TASK 3: Creare servizio JWT
  - File: services/jwt_service.py
  - Dipendenze: Task 2
  - Risk: MEDIUM

TASK 4: Middleware autenticazione
  - File: middleware/auth_middleware.py
  - Dipendenze: Task 3
  - Risk: MEDIUM

TASK 5: Test suite completa
  - File: tests/test_auth.py
  - Dipendenze: Task 4
  - Risk: LOW
```

Ogni task contiene:
- Descrizione chiara
- File e funzioni coinvolte
- Livello di rischio (LOW/MEDIUM/HIGH)
- Dipendenze verso altri task

---

### **Coding Agent**

Implementa modifiche al codice.

**Responsabilità:**
- Generazione e modifica file
- Applicazione di patch intelligenti
- Rispetto regole del progetto
- Output in formato diff applicabile

**NON decide architettura** — segue il piano del Planner.

---

### **Testing Agent**

Esecuzione di pipeline di validazione completa.

**Responsabilità:**
- Test automatico (unit, integration, E2E)
- Lint e static analysis
- Branch coverage e mutation testing
- Debugging automatico di fallimenti

**Un task è completato SOLO quando:**

```
Codice generato
    ↓
Lint check
    ↓
Test execution
    ↓
Code review
    ↓
Aggiornamento memoria
    ↓
✓ COMPLETATO
```

---

### **Reviewer Agent**

Valutazione qualitativa del codice.

**Responsabilità:**
- Analisi qualità del codice
- Verifica conformità regole
- Individuazione problemi di design
- Proposte di miglioramento

---

### **Memory Agent**

Gestione della conoscenza persistente del progetto.

**Memoria strutturata in `.ai/` folder:**
- `project.md` — descrizione generale e stack
- `architecture.md` — decisioni architetturali e dipendenze
- `rules.md` — convention di codice e best practice
- `glossary.md` — termini e concetti specifici del progetto
- `memory/` — episodic, semantic, procedural memory
- `knowledge/` — knowledge base e RAG index

---

### **Security Agent**

Sicurezza integrata nel ciclo di sviluppo.

**Responsabilità:**
- STRIDE threat modeling
- SAST (Static Application Security Testing)
- Analisi dipendenze e secret detection
- Policy enforcement automatica

---

### **Research Agent**

Acquisizione di conoscenza da fonti esterne.

**Responsabilità:**
- Ricerca documentazione ufficiale
- Analisi repository GitHub
- Valutazione librerie alternative
- Aggiornamento knowledge base

---

### **Supervisor Agent** (Orchestratore)

Nodo centrale del sistema — LangGraph orchestratore.

**Responsabilità:**
- Interpretazione richieste naturali
- Routing verso agenti corretti
- Gestione stato globale
- Quality gate e approvazioni umane
- Escalation per decisioni critiche

---

## 📁 Struttura progetto

```
AIAgent/
├── .ai/                                    # Brain del progetto
│   ├── code agent documentation/           # 58+ documenti di specifica
│   │   ├── 1. fundamentals.md
│   │   ├── 2. structure.md
│   │   ├── 3. analisisys.md
│   │   └── ... (59 file totali)
│   ├── project.yaml                        # Config principale
│   ├── architecture.md                     # Decisioni architetturali
│   ├── rules.md                            # Convention di codice
│   ├── glossary.md                         # Termini specifici
│   ├── memory/
│   │   ├── episodic.md                    # Cronaca degli eventi
│   │   ├── semantic.md                    # Conoscenza strutturata
│   │   └── procedural.md                  # Come fare le cose
│   ├── knowledge/                          # Knowledge base RAG
│   ├── prompts/                            # Prompt templates
│   └── logs/                               # Audit trail agenti
│
├── core/                                   # Core del sistema
│   ├── __init__.py
│   ├── Agent.py                           # LangGraph orchestratore
│   ├── LLM.py                             # Gestione Ollama e modelli
│   └── nodes/                             # Nodi specializzati
│       ├── shared.py                      # Stato condiviso
│       ├── memory/
│       │   ├── memory.py
│       │   └── long_term_memory.py
│       ├── planning/
│       │   ├── planning.py
│       │   └── paln.py
│       ├── reasoning/
│       │   ├── reasoning.py
│       │   └── declination.py
│       ├── executor/
│       │   └── executor.py
│       ├── critic/
│       │   └── critic.py
│       └── final/
│           └── final.py
│
├── tools/                                  # Tool layer operativo
│   ├── tools.py                           # Tool registry
│   └── categories/general/
│       ├── bookshelf.py                   # Ricerca knowledge base
│       ├── calculator.py                  # Calcoli matematici
│       ├── datetime_tool.py               # Data e ora
│       ├── introspection.py               # Analisi agente
│       ├── remember.py                    # Memoria persistente
│       ├── speech_to_text.py              # Trascrizione audio
│       └── text_to_speech.py              # Sintesi vocale
│
├── knowledge/                             # Knowledge base
│   ├── bookshelf/                         # Documentazione
│   │   ├── manual.txt
│   │   └── password.txt
│   └── IO/                                # Memoria agente
│       ├── agent_memory.md
│       ├── general_memory.md
│       ├── personality.md
│       ├── role.md
│       └── tts_output/
│
├── main.py                                # Entry point
├── test.py                                # Test suite
├── requirements.txt                       # Dipendenze
└── README.md                              # Questo file
```

---

## 🚀 Quick start

### Prerequisiti

- Python 3.11+
- Ollama installato e in esecuzione
- AMD RX 6800 XT (o GPU compatibile)
- 16GB VRAM minimo

### Installazione

```powershell
# Clona il repository
git clone <repo-url>
cd AIAgent

# Crea ambiente virtuale
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installa dipendenze
python -m pip install --upgrade pip
pip install -r requirements.txt

# Tool audio (opzionali ma consigliati)
pip install SpeechRecognition gTTS pydub

# Configura Ollama
ollama pull qwen2:4b
ollama pull qwen2:coder
ollama serve  # In terminale separato
```

### Avvio

```powershell
python main.py
```

Digita comandi in linguaggio naturale:

```
Tu: Aggiungi autenticazione JWT al backend

Agente: 
[Analyzing project structure...]
[Planning 5 tasks with dependencies...]
[Request human approval for MEDIUM-risk tasks...]
[Awaiting confirmation...]
```

Comandi di uscita: `exit`, `quit`, `q`

---

## 🔄 Flusso di lavoro completo

### 1️⃣ **Ricezione richiesta**
L'utente inserisce un comando naturale in chat.

### 2️⃣ **Comprensione e planning**
- **Memory Agent** retrieves contesto del progetto
- **Architect Agent** propone soluzione
- **Planner Agent** decompone in task atomici
- **Supervisor** richiede approvazione se rischio >= MEDIUM

### 3️⃣ **Implementazione**
- **Coding Agent** genera/modifica file
- **Testing Agent** esegue validazione completa
- **Critic Agent** verifica qualità

### 4️⃣ **Review e commit**
- **Reviewer Agent** approva o richiede modifiche
- **Git Agent** crea branch, commit e PR
- **Deployment Agent** esegue rilascio se approvato

### 5️⃣ **Aggiornamento memoria**
- **Memory Agent** aggiorna `.ai/` folder
- **Research Agent** acquisisce nuove conoscenze
- Knowledge base evolve con il progetto

---

## 📊 Metriche e valutazione

Monitoraggio continuo via **LangSmith**:

### Qualità del codice
- **Cyclomatic Complexity** < 8
- **Maintainability Index** > 80
- **Duplication Rate** < 5%
- **Test Coverage** > 80%

### Performance agenti
- **First Pass Success Rate** (FPSR) — codice corretto al primo tentativo
- **Regression Rate** — errori introdotti
- **Plan Accuracy** — decomposizione corretta di task
- **Human Intervention Rate** — % approvazioni richieste

---

## 🔐 Sicurezza

### Sandboxing
- Esecuzione codice in ambienti isolati
- Rollback automatico via git su fallimento
- Timeout su operazioni lunghe

### Permessi granulari
- **Read** — accesso codebase
- **Write** — modifica file
- **Execute** — esecuzione test e tool

### Operazioni che richiedono conferma umana
- Modifiche architetturali (HIGH risk)
- Eliminazione di file/branch
- Deployment in produzione
- Decisioni di design

---

## 📚 Documentazione

Consultare i **59 documenti di specifica** in `.ai/code agent documentation/`:

| Fase | Documenti | Tema |
|------|-----------|------|
| **Fondazioni** | 1–9 | Principi, stack, workflow, MVP roadmap |
| **Design MVP** | 10–15 | Prototipo v1/v2/v3, hardware, UI, security |
| **Layer avanzati** | 16–22 | Memoria, reasoning, collaborazione, testing, git, deployment |
| **Agenti specializzati** | 23–32 | PO, Security, Research, Memory, Tool, Runtime, Evaluation |
| **Implementazione** | 33–46 | Agenti avanzati, code intelligence, deployment, evaluation |
| **Infrastruttura** | 47–55 | Ollama, chat interface, database, integrazione |
| **Validazione** | 56–58 | MVP reale, roadmap LV1-3, checklist v1.0 |
| **Master Roadmap** | 59 | ROADMAP.md — lista ordinata di task con checkbox |

---

## 🎓 Filosofia di design

L'agente ragiona **come un member esperto di un team software**:

```
Prima di modificare:

1. ✓ Comprende il problema
2. ✓ Analizza il progetto
3. ✓ Valuta impatto
4. ✓ Propone soluzione
5. ? Attende approvazione (se necessario)
6. ✓ Implementa
7. ✓ Verifica
8. ✓ Aggiorna conoscenza
```

---

## 📞 Supporto e contributi

Per problemi o suggerimenti, consulta:
- Documentazione in `.ai/code agent documentation/`
- ROADMAP.md in `.ai/code agent documentation/59. ROADMAP.md`
- Issue tracker del progetto

---

## 📄 Licenza

[Inserire licenza]

---

**Ultima modifica:** 2026-07-13  
**Versione:** MVP v0.1 (in development)  
**Status:** 🔨 Fase 0 — Fondazioni in progress  
**Documento di riferimento:** `.ai/code agent documentation/1. fundamentals.md`
