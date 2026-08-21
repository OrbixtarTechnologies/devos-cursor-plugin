---
name: debugging
description: Diagnose bugs systematically using reproduction, evidence, hypothesis ranking, and regression verification.
---
# Debugging

## Workflow
1. Establish the exact symptom and reproduction.
2. Capture logs, stack traces, inputs, versions, and environment facts.
3. Build a short hypothesis tree ranked by evidence.
4. Trace execution to the first incorrect state, not merely the final error.
5. Fix root cause with minimal scope.
6. Add a regression test when practical.
7. Re-run the original reproduction and broader affected checks.

## Rule
Do not hide an intermittent or environmental failure behind retries without understanding it.
