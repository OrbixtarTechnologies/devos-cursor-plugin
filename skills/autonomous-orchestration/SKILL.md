---
name: autonomous-orchestration
description: Decompose multi-concern work into a task graph, delegate to DevOS specialists, and verify the outcome.
---

## Use when
The request spans multiple concerns, repositories, systems, or more than a few files.

## Procedure
1. Discover context.
2. Build task graph with dependencies, ownership, risk, and verification.
3. Delegate independent work to specialist subagents (`devos-architect`, `devos-implementer`, `devos-debugger`, `devos-reviewer`, `devos-security`, `devos-test`, `devos-docs`, `devos-ci-operator`, `devos-product-integrator`, `devos-observability`).
4. Merge findings before edits that cross boundaries.
5. Implement with explicit checkpoints.
6. Run verification gates.
7. Persist durable knowledge in `.devos/` when appropriate.

## Deliverable
Return task graph, delegated roles, key findings, changes, verification evidence, and unresolved risks.
