# AI Software Engineer Agent — Architecture

## Versione

**Current:** 1.0 (MVP Foundation)  
**Last Updated:** 2026-07-13

---

## Componenti principali

### 1. LLM Runtime (Ollama)

**Responsabilità:**
- Gestione modelli locali
- Inferenza con quantizzazione
- API REST per tool calling

**Modelli:**
- `qwen2:4b` — Planner/Router (orchestrazione)
- `qwen2:coder` — Coder Agent (generazione codice)
- `gemma:latest` — Reviewer Agent (code review)
- `deepseek-r1` — Reasoning Agent (decisioni complesse)

**Hardware target:**
- AMD RX 6800 XT 16GB VRAM
- ROCm backend per AMD GPU

---

### 2. Framework Agentico (LangGraph + LangChain)

**Stato globale:**
```python
class AgentState(TypedDict):
    input: str
    chat_history: list[dict]
    project_context: dict
    current_task: dict
    plan: list[dict]
    code_changes: dict
    test_results: dict
    approvals: list[dict]
    errors: list[dict]
    output: str
```

**Nodi del grafo:**

```
memory → reasoner → planner → executor → critic → (planner | final)
   ↑                                         ↓
   └─────────────────────────────────────────
   
final → END
```

**Nodi specializzati:**

1. **Memory Node** — retrieval contesto del progetto
2. **Reasoner Node** — decide se usare tool
3. **Planner Node** — scompone in task
4. **Executor Node** — esegue tool
5. **Critic Node** — valida e decide retry
6. **Final Node** — genera risposta

---

### 3. Code Intelligence Layer

**AST Parsing:**
- Tool: `tree-sitter` (multi-language)
- Linguaggi: Python, JavaScript, Go, Rust, Java

**Dependency Graph:**
- Costruito durante parsing
- Aggiornato ad ogni modifica validata
- Export: JSON, GraphML

**Vector Database:**
- Backend: `ChromaDB` (dev), `FAISS` (performance)
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Indicizzazione: funzioni, classi, commenti, doc

---

### 4. Memory System

**Struttura:**

```
.ai/
├── project.md              # Descrizione progetto
├── architecture.md         # Questo file
├── rules.md               # Regole e convenzioni
├── glossary.md            # Indice funzioni/classi
├── state.json             # Stato corrente
│
├── decisions/             # ADR (Architecture Decision Records)
│   ├── ADR-001-*.md
│   └── ADR-002-*.md
│
├── tasks/                 # Ciclo di vita task
│   ├── active/
│   │   └── task_NNN/
│   │       ├── request.md
│   │       ├── plan.yaml
│   │       ├── changes.diff
│   │       └── review.md
│   └── completed/
│
├── memory/                # Memoria agente
│   ├── short_term.md     # Task corrente
│   └── context.md        # Contesto operativo
│
├── knowledge/             # Conoscenza strutturata
│   ├── modules.yaml
│   ├── functions.yaml
│   ├── classes.yaml
│   └── impact_map.json
│
├── graph/                 # Dependency graph
│   └── dependency_graph.json
│
├── vector/                # Vector DB (gitignored)
│   └── chroma_db/
│
├── prompts/               # Prompt templates
│   ├── system_*.txt
│   ├── planner_*.txt
│   └── coder_*.txt
│
└── logs/                  # Audit trail (gitignored)
    └── YYYY-MM-DD/
        └── task_NNN/
```

---

## Flusso dati tra componenti

### Ricezione richiesta utente

```
User Input (chat)
    ↓
Memory Node [retrieval contexto da .ai/]
    ↓
Reasoner Node [decide orchestrazione]
    ↓
Planner Node [scompone in task]
    ↓
[HUMAN APPROVAL se risk >= MEDIUM]
    ↓
Executor Node [genera/modifica codice]
    ↓
Critic Node [esegue test/lint]
    ↓
[retry loop se fallimento]
    ↓
Final Node [genera risposta]
    ↓
Memory Node [aggiorna .ai/]
    ↓
User Output (chat)
```

### Aggiornamento memoria

Post-validazione ogni task:

```
Modified Files
    ↓
AST Parsing (tree-sitter)
    ↓
Dependency Graph Update
    ↓
Vector DB Reindex (ChromaDB)
    ↓
glossary.md Update
    ↓
architecture.md Update (if needed)
    ↓
state.json Update
    ↓
Git Commit
```

---

## Interfaccia utente (MVP v0.1)

**MVP uses CLI chat** (no web UI yet)

```
Tu: Aggiungi autenticazione JWT

Agente:
[Memory] Analyzing project structure...
[Planner] Decomposing into 5 tasks...
[Approval] Waiting for HIGH risk confirmation...

Tu: Approve

[Executor] Generating code...
[Critic] Running tests... ✓ PASSED
[Final] Done! Branch: feature/jwt-auth
```

Future: Web interface (FastAPI + React)

---

## Decisioni architetturali attuali

### 1. Local-First

✅ **Decision:** Everything runs locally, zero cloud dependencies  
✅ **Consequence:** Ollama for LLM, SQLite for state, local vector DB  
✅ **Trade-off:** Higher setup complexity vs privacy/control

### 2. Human-in-the-Loop

✅ **Decision:** Explicit approval for HIGH risk changes  
✅ **Consequence:** Planner marks risk level per task  
✅ **Trade-off:** Slower execution vs safety

### 3. LangGraph over LangChain

✅ **Decision:** Use LangGraph for orchestration (not just LangChain chains)  
✅ **Consequence:** Explicit state machine, checkpoint/recovery support  
✅ **Trade-off:** More verbose vs better control

### 4. Trunk-Based Development

✅ **Decision:** feature branches, short-lived, frequent merges to main  
✅ **Consequence:** CI/CD must be strong, early detection of conflicts  
✅ **Trade-off:** More discipline vs simpler workflow

---

## Integrazione con strumenti esterni

### Git

- Branch creation automatica (feature/xyz)
- Commit generation automatica (structured format)
- PR generation automatica con review request

### LangSmith

- Tracing di tutte le chiamate LLM
- Metriche per ogni agente
- Feedback loop per ottimizzazione

### Ollama

- Gestione modelli (pull, list, info)
- Model swapping basato su task complexity
- Quantizzazione automatica Q4/Q5

---

## Performance targets

### Latency

- **Ricezione richiesta → Risposta:** < 30 sec (per task semplice)
- **LLM inference:** < 10 sec per risposta (Q4 quantizzazione)
- **Tool execution:** < 5 sec (file read/write)

### Resource usage

- **VRAM:** < 12GB (lasciare headroom per sistema)
- **CPU:** < 80% (non strangolare sistema)
- **Disk:** < 20GB per vector DB + logs

---

## Testing strategy

### Unit tests

- Mock LLM responses (non esecuzione reale Ollama)
- Test logica agenti in isolamento
- Coverage: >= 80%

### Integration tests

- Real Ollama connection
- Real file system operations
- Test workflow end-to-end

### E2E tests

- Complete user workflow
- Real project modification
- Validation tramite test suite progetto

---

## Deployment topology (future)

```
Local Machine (MVP)
    Ollama (LLM)
    LangGraph Agent
    SQLite DB
    Vector DB (ChromaDB)
    CLI Interface

Production (Future v1.1+)
    Docker container
    Ollama service
    FastAPI backend
    PostgreSQL DB
    Vector DB (FAISS)
    Web UI (React)
```

---

## Backup e disaster recovery

**Backup strategy:**

- `.ai/` folder → daily backup (version control via git)
- Database state → daily export to JSON
- Vector DB → regenerable from source code

**Recovery:**

- On crash: restore from last git commit
- On LLM error: retry con fallback model
- On tool failure: rollback file operations

---

**Versione:** 1.0  
**Ultima modifica:** 2026-07-13  
**Responsabile:** AI Software Engineer Agent Project

