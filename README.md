# DevOS for Cursor

A production-grade Cursor plugin for context-first engineering, specialist delegation, verification, security review, and repository intelligence.

## What it adds

**Rules** — persistent quality, architecture, testing, security, Git, documentation, performance, memory, verification, integrations, and orchestration guidance.

**Skills** — context discovery, planning, implementation, debugging, review, security audit, testing, refactoring, documentation, release readiness, project memory, architecture intelligence, CI intelligence, observability, integration context, and autonomous orchestration.

**Subagents** — orchestrator, architect, implementer, debugger, reviewer, security, test, docs, CI operator, product integrator, and observability specialists.

**Commands** — `devos-context`, `devos-plan`, `devos-implement`, `devos-debug`, `devos-review`, `devos-test`, `devos-security`, `devos-release`, `devos-orchestrate`, `devos-memory`, `devos-architecture`, `devos-ci`, `devos-integrate`, `devos-observe`.

**MCP** — `devos-project-intel` exposes repository structure, file search, package metadata, test discovery, Git status, project memory, and architecture signals without adding destructive capabilities.

**Hook** — a lightweight advisory guard calls out destructive prompts but does not block work.

## Install locally

Copy this directory to:

`~/.cursor/plugins/local/devos/`

Then reload Cursor. Prefer copying the real directory rather than symlinking for local development because current Cursor plugin behavior has documented symlink issues.

This repository can stay at its development path. Local install is a copy into `~/.cursor/plugins/local/devos/` so Cursor can discover the plugin.

## Use

- Start with `/devos-context` for an unfamiliar repository.
- Use `/devos-plan` before substantial feature work.
- Use `/devos-orchestrate` for multi-file or cross-cutting work.
- Use `/devos-review` after implementation.
- Use `/devos-security` for security-sensitive changes.
- Use `/devos-release` before shipping.

## Design principles

1. Evidence over confidence.
2. Small diffs over rewrites.
3. Verification before completion claims.
4. Explicit uncertainty.
5. Least privilege for tool access.
6. Independent review for high-risk changes.

## Project memory

DevOS stores durable, non-secret project context in `.devos/` inside the target repository:

- `.devos/project.md`
- `.devos/architecture.md`
- `.devos/decisions.md`
- `.devos/worklog.md`

Initialize or refresh it with `/devos-memory`. Never store credentials or personal data there.

If you used an earlier build that wrote project memory under a different directory name, rename that directory to `.devos/` before continuing.

## Marketplace

The manifest follows Cursor's current plugin layout: `.cursor-plugin/plugin.json` plus discoverable `skills/`, `rules/`, `agents/`, `commands/`, `hooks/`, and MCP configuration.

## License

MIT.

## DevOS 2.1

Version 2.1 is the DevOS-branded release of the 2.0 orchestration system: a controller, durable `.devos/` project memory, architecture intelligence, CI/observability workflows, and optional GitHub/Linear/Vercel/Sentry integration context. External integrations remain opt-in and read-only by default.

### Recommended operating pattern

Use `/devos-orchestrate` for complex work. Use `/devos-memory` to initialize durable context, `/devos-architecture` for system mapping, `/devos-ci` for failed checks, and `/devos-integrate` to gather external project context.
