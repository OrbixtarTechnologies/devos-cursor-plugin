# Installation

## Local development

Copy the entire `devos` plugin directory to:

`~/.cursor/plugins/local/devos/`

Then reload Cursor.

The development checkout may live elsewhere. Cursor discovers local plugins from `~/.cursor/plugins/local/devos/`.

## Notes

The MCP server uses the system Python interpreter and standard library only. On systems where `python` resolves differently, change `mcp.json` to the appropriate interpreter command.

The plugin is intentionally read-heavy and write-light: the MCP server exposes repository intelligence but no file mutation or arbitrary shell execution tools.

## First commands

`/devos-context`

`/devos-plan`

`/devos-implement`

`/devos-review`

`/devos-release`

## Additional commands

`/devos-orchestrate` `/devos-memory` `/devos-architecture` `/devos-debug` `/devos-test` `/devos-security` `/devos-ci` `/devos-integrate` `/devos-observe`
