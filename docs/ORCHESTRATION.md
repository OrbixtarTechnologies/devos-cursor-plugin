# DevOS Orchestration

DevOS uses a controller-and-specialists model.

## Execution graph
`Context → Intent → Plan Graph → Parallel Discovery → Coordinated Implementation → Verification → Memory → Report`

### Parallelism
Parallelize read-only or independent tasks such as architecture discovery, security review, test reconnaissance, and integration context. Do not parallelize conflicting edits.

### Evidence model
Every delegated task returns:
- objective
- scope/files
- findings
- evidence
- changes (if any)
- verification
- risks/blockers

### Conflict resolution
The orchestrator owns the final decision. Prefer repository evidence, tests, and explicit product requirements over agent preference.

### Specialists
Delegate to `devos-architect`, `devos-implementer`, `devos-debugger`, `devos-reviewer`, `devos-security`, `devos-test`, `devos-docs`, `devos-ci-operator`, `devos-product-integrator`, or `devos-observability` when the work is separable.
