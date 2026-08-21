---
name: context-discovery
description: Build a concise, evidence-backed map of a repository before implementation.
---
# Context Discovery

## Goal
Turn an unfamiliar repository into a reliable working context without reading everything.

## Workflow
1. Inspect top-level structure and manifests.
2. Find repository instructions and development scripts.
3. Identify the execution path for the requested behavior.
4. Trace imports/calls into the relevant modules and tests.
5. Inspect CI or deployment configuration when operational behavior matters.
6. Return a compact context map: architecture, relevant files, commands, constraints, risks, and unknowns.

## Guardrails
Never invent architecture from filenames alone. Mark uncertainty explicitly.
