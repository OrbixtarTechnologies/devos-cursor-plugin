---
name: test-engineering
description: Design and execute proportionate unit, integration, contract, and end-to-end verification.
---
# Test Engineering

Choose the cheapest test that proves the behavior, then add higher-level tests where integration risk warrants it. Cover happy path, boundary conditions, failure handling, permissions, state transitions, and regression cases.

Prefer deterministic tests. Isolate external dependencies with project-approved fakes/mocks/fixtures. Do not make tests weaker merely to avoid failure.
