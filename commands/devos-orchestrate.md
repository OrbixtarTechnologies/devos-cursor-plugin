---
name: devos-orchestrate
description: Run the full DevOS orchestration workflow for the current request.
---
# DevOS Orchestrate
Run the full DevOS orchestration workflow for the current request.

Steps: inspect context → build task graph → delegate → execute → verify → update memory → report. Use specialist subagents where valuable. Prefer `devos-orchestrator` as the controller.
