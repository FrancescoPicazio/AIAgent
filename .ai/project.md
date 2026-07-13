# AI Software Engineer Agent — Project Definition

## Progetto

**Nome:** AI Software Engineer Agent  
**Versione:** MVP v0.1  
**Status:** In development (Fase 0 — Fondazioni)  
**Data creazione:** 2026-07-13

---

## Obiettivo

Realizzare un agente AI **autonomo e locale** che agisce come un software engineer senior di livello enterprise. L'agente deve comprendere, progettare e modificare progetti software complessi con supervision umana continua.

### Capacità richieste

L'agente deve essere in grado di:

- ✅ Analizzare requisiti descritti in linguaggio naturale
- ✅ Comprendere progetti software esistenti
- ✅ Progettare nuove funzionalità
- ✅ Suddividere il lavoro in task atomici con dipendenze
- ✅ Modificare codice seguendo regole del progetto
- ✅ Eseguire test e validazioni automatiche
- ✅ Correggere errori in loop automatico
- ✅ Mantenere memoria persistente del progetto
- ✅ Documentare modifiche in modo semantico
- ✅ Richiedere approvazione umana nei punti critici

### Non è

- Non è un semplice generatore di codice
- Non è un chatbot da assistenza al coding
- Non produce solo snippet di codice
- Non automatizza senza controllo umano

---

## Stack tecnologico

### Runtime LLM

- **Ollama** — inferenza locale con modelli quantizzati
- **Modelli:** Qwen3 4B (orchestrazione), Qwen3-Coder (coding), Gemma (review), DeepSeek (reasoning)
- **Hardware:** AMD RX 6800 XT 16GB VRAM (ROCm per AMD)
- **Quantizzazione:** Q4/Q5 per efficienza

### Framework Agentico

- **LangChain** — gestione tool, prompt, RAG, memoria
- **LangGraph** — orchestrazione workflow multi-agente, grafo degli agenti, stato globale
- **Python 3.11+** — linguaggio di implementazione
- **FastAPI** (opzionale per v1.1) — API REST per interfaccia utente

### Database e memoria

- **SQLite** — database locale per stato e task history (dev)
- **PostgreSQL** — produzione (future)
- **ChromaDB / FAISS** — vector database per RAG
- **JSON** — configurazione e stato persistente

### Monitoring e valutazione

- **LangSmith** — tracciamento LLM, metriche di qualità, benchmark
- **Logging locale** — audit trail, debug, trace agenti

### Versioning e deployment

- **Git** — versionamento, branch strategy
- **Docker** (future) — containerizzazione
- **GitHub Actions / CI/CD** (future) — pipeline automazione

---

## Vincoli principali

### 1. Local First 🔒

- **Tutto locale:** nessun codice esce dalla macchina
- **No cloud dependencies:** nessuna dipendenza obbligatoria da API esterne
- **Privacy:** controllo totale dei dati
- **Personalizzazione:** agente altamente customizzabile per il progetto

### 2. Human in the Loop 👤

- **Approvazione finale:** utente sempre ha ultima parola
- **Decisioni critiche:** architettura e design richiedono conferma
- **Escalation:** agente sa quando escalare a umano
- **Reversibilità:** ogni azione può essere rollback tramite git

### 3. Replicabilità

- **Documentazione viva:** specifica `.ai/` evolvendo con il progetto
- **Determinismo:** gli agenti generano sempre output prevedibili
- **Traceabilità:** ogni decisione è registrata in ADR
- **Reproducibilità:** same input = same output (con seed LLM)

---

## Requisiti fondamentali

### Architettura

- [ ] Sistema multi-agente con LangGraph
- [ ] Stato globale condiviso tra agenti
- [ ] Routing dinamico verso agenti specializzati
- [ ] Supervisor orchestratore centrale
- [ ] Checkpoint e recovery da crash

### Memoria

- [ ] Memoria strutturata in `.ai/` folder (project.md, rules.md, glossary.md, etc.)
- [ ] Vector database per semantic search
- [ ] Knowledge graph per dipendenze
- [ ] History e audit trail
- [ ] Aggiornamento automatico post-validazione

### Code Intelligence

- [ ] AST parsing con tree-sitter (Python, JavaScript, Go, Rust)
- [ ] Dependency graph construction
- [ ] Impact analysis automatica
- [ ] Semantic understanding di funzioni e classi
- [ ] Refactoring suggestions

### Testing e QA

- [ ] Generazione automatica test (unit, integration, E2E)
- [ ] Execution loop con debugging automatico
- [ ] Branch coverage e mutation testing
- [ ] Quality gate pre-commit
- [ ] First Pass Success Rate (FPSR) tracking

### Sicurezza

- [ ] Sandboxing esecuzione codice
- [ ] Permessi granulari (read, write, execute)
- [ ] Secret detection e policy enforcement
- [ ] SAST e threat modeling STRIDE
- [ ] Rollback automatico su fallimento

### Git Integration

- [ ] Branch strategy automatica
- [ ] Commit message intelligenti (Summary/Changes/Tests/Risk)
- [ ] PR generation e code review
- [ ] Auto-merge con criteri configurabili
- [ ] Squash commits intelligente

### UI/UX

- [ ] Chat interface nel progetto
- [ ] Dashboard stato workflow
- [ ] Approval flow con context
- [ ] Streaming risposta LLM in tempo reale
- [ ] Log agenti consultabili

---

## Fasi di sviluppo

### Fase 0 — Fondazioni (CURRENT)
Principi, stack, struttura `.ai/`, README, documentazione specifica.

### Fase 1 — Design MVP
Prototipo v1/v2/v3, ottimizzazione hardware, UI base, security layer.

### Fase 2 — Layer avanzati
Memoria a lungo termine, reasoning layer, collaborazione multi-agente.

### Fase 3 — Agenti specializzati
PO Agent, Security Agent, Research Agent, Memory Agent, Tool Agent, Supervisor.

### Fase 4 — Implementazione avanzata
Agenti con versioning interno, code intelligence engine, deployment pipelines.

### Fase 5 — Infrastruttura & integrazione
Ollama tuning, chat interface, database interno, integrazione LangGraph completa.

### Fase 6 — Validazione e MVP reale
Implementazione concreta primo MVP, roadmap LV1-3, checklist finale v1.0.

---

## Metriche di successo

### Agente

- **First Pass Success Rate (FPSR):** >= 70% (codice corretto al primo tentativo)
- **Regression Rate:** <= 5% (errori introdotti)
- **Human Intervention Rate:** <= 20% (richieste approvazione)
- **Mean Time To Fix (MTTF):** < 5 min

### Codice

- **Cyclomatic Complexity:** < 8
- **Maintainability Index:** > 80
- **Duplication Rate:** < 5%
- **Test Coverage:** > 80%

### Planning

- **Plan Accuracy:** >= 80% (decomposizione corretta)
- **Task Completeness:** 100% (nessun task orfano)
- **Dependency Accuracy:** >= 95%

---

## Dipendenze e prerequisiti

### Hardware

- GPU: AMD RX 6800 XT 16GB (consigliato) o compatibile
- CPU: Ryzen 7 5800X o superiore
- RAM: 32GB (16GB minimo)
- SSD: 500GB libero

### Software

- Python 3.11+
- Ollama
- Git
- Docker (future)

### Librerie core

Vedi `requirements.txt` principale del progetto.

---

## Contatti e risorse

- **Documentazione:** `.ai/code agent documentation/` (59+ documenti)
- **Master Roadmap:** `.ai/code agent documentation/59. ROADMAP.md`
- **Repository:** GitHub (privato durante MVP)
- **Team:** Sviluppatore principale + Copilot AI

---

**Ultima modifica:** 2026-07-13  
**Responsabile:** AI Software Engineer Agent Project  
**Prossima review:** Post-completamento Fase 1

