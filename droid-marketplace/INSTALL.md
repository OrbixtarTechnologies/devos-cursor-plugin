# Cursor → Factory Droid marketplace

This repository contains a bridge that converts the official Cursor plugin marketplace into a Factory Droid marketplace.

## Generate or refresh the marketplace

From the repository root:

```bash
python3 scripts/sync_cursor_droid_marketplace.py
```

On Windows PowerShell:

```powershell
py scripts/sync_cursor_droid_marketplace.py
```

The generated marketplace is written to `droid-marketplace/`.

## Register it locally with Droid

Factory can add a local marketplace directly:

```bash
droid plugin marketplace add ./droid-marketplace
droid plugin marketplace list
```

Then open:

```text
/plugins
```

or install directly:

```bash
droid plugin install <plugin-name>@cursor-droid --scope user
```

## Register the Git-hosted subdirectory

Factory supports Git subdirectory marketplaces through `extraKnownMarketplaces`:

```json
{
  "extraKnownMarketplaces": {
    "cursor-droid": {
      "source": {
        "source": "git-subdir",
        "url": "https://github.com/OrbixtarTechnologies/devos-cursor-plugin.git",
        "path": "droid-marketplace",
        "ref": "main"
      }
    }
  }
}
```

Once generated content has been committed, Droid will treat it as a normal marketplace and plugin IDs use the form `plugin-name@cursor-droid`.

## Compatibility behavior

The adapter:

- adds `.factory-plugin/plugin.json` to each mirrored plugin;
- copies Cursor `agents/` into Factory `droids/`;
- maps `CURSOR_PLUGIN_ROOT` references to `DROID_PLUGIN_ROOT`;
- copies `.mcp.json` to `mcp.json` when needed;
- preserves Cursor-only `rules/` but does not claim Droid loads them;
- flags plugins containing rules or hooks as partial in `compatibility.json`.

The official Cursor repository remains the upstream source.
