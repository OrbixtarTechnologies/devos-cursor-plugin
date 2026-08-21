---
name: code-review
description: Perform a rigorous evidence-based review for correctness, security, maintainability, compatibility, and missing tests.
---
# Code Review

Review in this order:
1. Correctness and behavioral regressions.
2. Security and authorization.
3. Data integrity and concurrency.
4. API compatibility and error handling.
5. Performance and operational impact.
6. Tests and observability.
7. Maintainability and clarity.

Report findings by severity with file/line evidence and a concrete fix. Do not report style preferences as defects.
