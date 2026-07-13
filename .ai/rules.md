aspet# AI Software Engineer Agent — Rules and Conventions

## Coding Rules

### General

1. **Python version:** 3.11+ (type hints obbligatori)
2. **Style:** PEP 8 (line length 100 chars max)
3. **Docstrings:** Google style per ogni funzione/classe
4. **Comments:** Spiegare il "perché", non il "cosa"

### Functions

Ogni funzione deve avere:

- **Docstring completa:**
  ```python
  def process_data(data: list[dict], timeout: int = 30) -> dict:
      """Process input data and return aggregated result.
      
      Args:
          data: List of data dictionaries to process.
          timeout: Maximum execution time in seconds.
          
      Returns:
          Dictionary with aggregated results.
          
      Raises:
          ValueError: If data is empty or malformed.
          TimeoutError: If processing exceeds timeout.
      """
  ```
- **Type hints completi** (input e output)
- **Error handling:** gestione di tutti i casi anomali
- **Logging:** tracciamento di operazioni critiche
- **Unit test:** minimo 80% coverage per funzione nuova

### Classes

- **Una responsabilità** (Single Responsibility Principle)
- **Dependency injection** per dipendenze
- **Immutabilità dove possibile** (dataclasses con frozen=True)
- **Protocol/ABC** per interface pubbliche

### Architecture

1. **Separation of concerns:** business logic ≠ infrastructure
2. **No circular dependencies:** import validation su CI
3. **Repository pattern** per data access
4. **Dependency injection** non hard-coded imports
5. **Configuration:** environment variables o config file, non constants

### Testing

- **TDD when possible:** test first, implementation second
- **Arrange-Act-Assert:** pattern chiarissimo nei test
- **Edge cases:** almeno 1 test per edge case
- **Error cases:** gestione errori deve essere testata
- **No flaky tests:** determinismo garantito
- **Fast execution:** unit test < 1ms, integration < 100ms

### Code Review

- **PR description:** cosa, perché, testing done
- **Commits granulari:** 1 commit = 1 logica
- **Branch naming:** `feature/xyz`, `bugfix/xyz`, `refactor/xyz`
- **No force push** a branch condivisi

---

## Architectural Rules

### Layering

L'architettura **deve** seguire questi layer:

```
Presentation Layer (API, CLI, WebSocket)
    ↓ depends on
Business Logic Layer (Services, Entities)
    ↓ depends on
Data Access Layer (Repository, ORM)
    ↓ depends on
Infrastructure Layer (Database, External Services)
```

**Regola:** Dipendenza SOLO verso layer inferiori, mai il contrario.

### Components

- **Agents:** nodi LangGraph, responsabilità chiara
- **Tools:** funzioni pure (input → output), no side effects
- **Services:** business logic, orchestrazione
- **Repository:** data access, queries
- **Models:** entity, DTO, database models

### Boundaries

- **Public API:** solo funzioni documentate
- **Private implementation:** _ prefix
- **Package boundaries:** imports chiari via `__init__.py`
- **No leaky abstractions:** dettagli implementativi nascosti

---

## Memory Management (.ai folder)

### What to update after EVERY validated change

**Dopo ogni task completato e validato:**

1. **glossary.md** — aggiungi funzioni/classi nuove
2. **architecture.md** — se cambia struttura
3. **graph/** — aggiorna dependency graph
4. **vector DB** — reindicizza su modifiche significative
5. **decisions/** — se nuova decisione architettuale
6. **state.json** — incrementa counters

### Don't update if

- Change not yet validated (before tests pass)
- Temporary fixes or rollback
- WIP branches

### Glossary entry template

```markdown
## FunctionName() / ClassName

**Location:** path/to/file.py

**Responsibility:** What it does

**Input:** Types and descriptions

**Output:** Return type and description

**Dependencies:** What it calls

**Impact:** LOW/MEDIUM/HIGH (modification impact)

**Test coverage:** Percentage

**Last modified:** By which task

**ADR:** Link to relevant architectural decision
```

---

## Security Rules

### Secrets Management

- **NO hardcoded secrets** (APIs, DB passwords, tokens)
- **Environment variables** for sensitive config
- **.env** file (never commit)
- **Secrets scanning** in CI/CD (pre-commit)

### Code Security

- **Input validation:** always sanitize external input
- **SQL injection:** use parameterized queries
- **CORS:** explicit domain whitelist
- **Rate limiting:** API endpoints must have limits
- **JWT:** tokens with exp, proper RS256 signing
- **HTTPS only:** no plain HTTP in production

### Data Privacy

- **GDPR compliant** (if EU users)
- **Encrypt at rest** (sensitive data)
- **Audit logging** for data access
- **Data minimization** (only collect needed data)

---

## Git Workflow

### Branch Strategy

**Trunk-Based Development for MVP:**

- `main` — sempre releasable, protected
- `feature/xyz` — feature branches, short-lived (< 1 week)
- `bugfix/xyz` — hotfixes, prioritized
- `refactor/xyz` — refactoring, no behavior change

### Commit Messages

Format:

```
[COMPONENT] Short description (50 chars max)

Detailed explanation if needed (wrap at 72 chars).

Related-To: #42 (task ID)
Changes: 
- Item 1
- Item 2

Risk: LOW/MEDIUM/HIGH

Test: What was tested
```

Example:

```
[Auth] Add JWT token refresh endpoint

Implements refresh token flow for automatic token renewal.
Users can now get new access token without re-login.

Related-To: #123
Changes:
- New endpoint POST /api/auth/refresh
- Refresh token storage in secure http-only cookie
- Token expiration validation

Risk: MEDIUM (authentication critical)

Test: 
- Unit: token generation and validation
- Integration: refresh flow with multiple clients
- E2E: login → token refresh → API call
```

### PR Requirements

Before merge:

- [ ] Tests passing (100% required)
- [ ] Code review approved (2+ approvals)
- [ ] No conflicts with main
- [ ] CI/CD pipeline green
- [ ] Performance benchmarks OK (if applicable)
- [ ] Documentation updated
- [ ] `.ai/` memory updated (glossary, architecture, etc.)

---

## Documentation Rules

### Code Documentation

- **Module docstring:** what the module does
- **Class docstring:** responsibility and public API
- **Function docstring:** what it does, not how
- **Type hints:** complete signatures
- **Examples:** for complex functions

### Project Documentation

- **README:** kept up-to-date in main branch
- **Architecture.md:** reflects current design
- **CONTRIBUTING.md:** for collaborators (future)
- **CHANGELOG.md:** semantic versioning

### ADR (Architecture Decision Record)

When to create:

- [ ] Major architectural decision
- [ ] Technology choice
- [ ] Pattern adoption
- [ ] Significant refactoring

Format: see `decisions/` folder template

---

## Deployment Rules

### Staging

- **Before merge:** deploy to staging equivalent
- **Smoke tests:** basic health checks
- **Performance:** benchmark against baseline
- **Rollback plan:** always have one

### Production

- **Canary deployment:** 10% → 50% → 100%
- **Monitoring:** logs, metrics, errors
- **Incident response:** clear escalation path
- **Rollback automation:** one-command rollback

---

## Review Checklist

Prima di approvare un PR:

### Correctness
- [ ] Logica corretta e completa
- [ ] Edge case gestiti
- [ ] Error handling presente
- [ ] No resource leaks

### Quality
- [ ] Codice leggibile e well-named
- [ ] Nessun codice duplicato
- [ ] Complessità ragionevole
- [ ] Performance accettabili

### Testing
- [ ] Test adequati e passanti
- [ ] Coverage >= 80%
- [ ] Flakiness zero
- [ ] Test nome descrittivi

### Documentation
- [ ] Docstring completate
- [ ] Comments per logica complessa
- [ ] Type hints presenti
- [ ] Examples se necessari

### Architecture
- [ ] Segue layer architetturali
- [ ] Nessuna violazione dipendenze
- [ ] Pattern consistency
- [ ] SOLID principles

### Security
- [ ] Nessun secret hardcoded
- [ ] Input validation present
- [ ] No injection vulnerabilities
- [ ] Auth/authorization corretta

---

**Versione:** 1.0  
**Ultima modifica:** 2026-07-13  
**Responsabile:** AI Software Engineer Agent Project

