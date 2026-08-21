---
name: integration-context
description: Gather optional GitHub, Linear, Vercel, and Sentry context without unauthorized mutations.
---

Use optional integrations to enrich engineering context:
- GitHub: issues, PRs, checks, releases
- Linear: project/issue intent and status
- Vercel: deployments, environments, build metadata
- Sentry: errors, releases, regressions

Read first. Mutate only with explicit authorization. Validate project/repo/environment identity before actions.
