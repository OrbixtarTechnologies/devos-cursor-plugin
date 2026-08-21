---
name: ci-intelligence
description: Diagnose CI/build failures, classify root cause, and apply the smallest safe fix with verification.
---

When CI is failing:
1. Identify exact failed job/check.
2. Reproduce locally where possible.
3. Correlate with changed files and recent dependency/config changes.
4. Classify root cause.
5. Apply smallest safe fix.
6. Re-run focused checks, then the broader gate.

Use optional GitHub/CI MCP data only when configured.
