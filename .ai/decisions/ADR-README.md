# Architecture Decision Record

## ADR Template

Use this template for all architectural decisions.

### Title

**ADR-XXX: [One-line summary of decision]**

---

### Status

- [ ] Proposed
- [ ] Accepted
- [x] Deprecated

---

### Context

What is the issue we're facing?

Why does this decision matter?

What alternatives were considered?

---

### Decision

We will [one-line summary].

Because [reasoning].

Trade-offs:
- Pro: [benefit 1]
- Pro: [benefit 2]
- Con: [drawback 1]
- Con: [drawback 2]

---

### Consequences

What will be the impact of this decision?

What becomes easier?

What becomes harder?

How do we validate this works?

---

### Related

- Links to other ADRs
- Links to documentation
- Links to issues/PRs

---

## ADR-001: Local-First Architecture (ACCEPTED)

**Status:** Accepted  
**Date:** 2026-07-13

### Decision

All components run locally. Zero cloud API dependencies.

### Rationale

- Privacy: No data leaves user machine
- Control: User owns infrastructure
- Personalization: Model can be fine-tuned for specific use case

### Impact

- More setup complexity for users
- Better performance (no network latency)
- Reproducible behavior
- Harder initial deployment

---

## ADR-002: Human-in-the-Loop for Critical Decisions (ACCEPTED)

**Status:** Accepted  
**Date:** 2026-07-13

### Decision

Architectural changes and HIGH-risk modifications require human approval.

### Rationale

- Safety: Prevent autonomous breaking changes
- Control: User decides strategy
- Learning: Understand agent reasoning

### Impact

- Slower feature development
- Better safety and control
- User must be available
- Easier to correct course

---

## ADR-003: LangGraph for Orchestration (ACCEPTED)

**Status:** Accepted  
**Date:** 2026-07-13

### Decision

Use LangGraph as main orchestration framework (not just chains).

### Rationale

- Explicit state machine
- Built-in checkpoint/recovery
- Multi-agent coordination
- Better error handling

### Impact

- More verbose than simple chains
- Better production readiness
- Easier debugging
- More powerful workflow patterns

---

**Next ADR:** ADR-004 (planned for Phase 1)

