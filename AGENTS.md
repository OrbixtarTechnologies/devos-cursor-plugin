# DevOS plugin maintainers

This repository is the DevOS Cursor plugin. Product name is **DevOS**. Manifest `name` is `devos`.

## Layout

- `.cursor-plugin/plugin.json` — plugin manifest
- `rules/` — always-on engineering contracts
- `skills/*/SKILL.md` — named workflows
- `agents/` — specialist subagents
- `commands/` — slash commands (`devos-*`)
- `hooks/` — advisory prompt guard
- `mcp.json` + `mcp/project_intel.py` — read-only repository intelligence
- `scripts/validate.mjs` — local quality gate

## Conventions

- User-facing name: DevOS
- Slugs, files, and slash commands: `devos` / `devos-*`
- Target-repo memory directory: `.devos/`
- MCP server: `devos-project-intel`
- Keep paths relative and inside this plugin directory
- Skills, rules, agents, and commands need YAML frontmatter (`name` + `description`; rules also need `alwaysApply`)

## Validate

```bash
npm run validate
```

Do not commit secrets. Do not add destructive MCP tools.
