# Task Management — Active Directory

## Struttura

```
tasks/
├── active/
│   └── task_NNN/
│       ├── request.md
│       ├── plan.yaml
│       ├── impact.md
│       ├── changes.diff
│       ├── tests.json
│       └── review.md
└── completed/
    └── (archived tasks)
```

## Template: request.md

```markdown
# Task #NNN: [Description]

**Requested by:** User (or Agent Planning)  
**Date:** YYYY-MM-DD  
**Priority:** LOW/MEDIUM/HIGH  

## Original Request

[User message or requirement]

## Context

[Any relevant project context]
```

## Template: plan.yaml

```yaml
task_id: 42
task_name: "Add JWT Authentication"
status: "in_progress"

risk_level: "MEDIUM"

affected_files:
  - path/to/file1.py
  - path/to/file2.py

affected_functions:
  - authenticate()
  - create_token()

steps:
  - name: "Create auth service"
    risk: "MEDIUM"
    dependencies: []
    
  - name: "Update user model"
    risk: "LOW"
    dependencies: ["step_0"]
    
  - name: "Add tests"
    risk: "LOW"
    dependencies: ["step_1"]

estimated_duration_minutes: 45
```

## Template: impact.md

```markdown
# Impact Analysis for Task #NNN

## Modified Functions

- `function_a()`: [what changed, impact]
- `function_b()`: [what changed, impact]

## Modified Classes

- `ClassA`: [changes]

## Dependency Impact

- Functions that call modified code: [list]
- Risk of regression: [assessment]

## Test Coverage

- New tests added: [count]
- Modified tests: [count]
- Coverage delta: [+X%]
```

---

**Note:** Active tasks should be short-lived (< 1 week each).

Archive completed tasks in `completed/` folder.

