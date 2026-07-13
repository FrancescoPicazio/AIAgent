# Memory — Short Term and Context

## short_term.md

Memoria temporanea per il task corrente.

### Contenuto

- Ragionamenti in corso
- File analizzati
- Problemi scoperti
- Possibili soluzioni
- State temporaneo

### Ciclo di vita

- **Creata:** all'inizio di ogni task
- **Aggiornata:** durante execution
- **Consultata:** dal Critic per validazione
- **Archiviata:** al completamento task
- **Eliminata:** se task abortito

### Esempio

```markdown
# Task #42: Add JWT Authentication

## Current state

Analyzing user model...
Found existing authentication in auth/service.py

## Files to modify

- [ ] models/user.py (add password hashing)
- [ ] auth/jwt_service.py (create new)
- [ ] tests/test_auth.py (create new)

## Issues found

- No password field in User model
- Old login code needs refactoring

## Proposed solution

1. Add password field with hashing
2. Create JWT service
3. Create tests
4. Update login endpoint

## Status

In progress - step 1 completed, step 2 in progress
```

---

## context.md

Memoria persistente a livello di sessione/progetto.

### Contenuto

- Informazioni utili recenti
- Stato generale dell'agente
- Contesto operativo
- Informazioni non strutturate

### Ciclo di vita

- **Creata:** all'inizio della sessione
- **Aggiornata:** dopo ogni task importante
- **Consultata:** prima di ogni nuova richiesta
- **Persiste:** tra sessioni

### Esempio

```markdown
# Project Context

## Recent developments

- Task #40: Refactored database layer
- Task #41: Added caching layer
- Task #42: In progress - JWT auth

## Current project state

Database is PostgreSQL, using SQLAlchemy ORM.
Frontend is React with TypeScript.

## Known issues

- Caching can get out of sync (TODO)
- Need performance testing on large datasets

## Team notes

User prefers PR-based workflow, 2+ approvals required.

## Last session

Session ended at 2026-07-12 19:30 UTC
User working on authentication feature
```

---

**Note:** Memory files are NOT versionat (gitignored).

Use for temporary state only.

For persistent knowledge, use `glossary.md` and `architecture.md`.

