# Cursor → Factory Droid Marketplace

This repository also hosts a generated Factory Droid-compatible mirror of Cursor's official plugin marketplace.

## Add the marketplace

Because this bridge currently lives in `devos-cursor-plugin`, the CLI derives the registered marketplace name from the repository:

```bash
droid plugin marketplace add https://github.com/OrbixtarTechnologies/devos-cursor-plugin
droid plugin marketplace list
```

Then install any mirrored plugin using the marketplace name reported by the second command, for example:

```bash
droid plugin install playwright@devos-cursor-plugin --scope user
droid plugin install github@devos-cursor-plugin --scope user
```

For a stable custom marketplace ID such as `cursor-droid`, declare it through Factory's `extraKnownMarketplaces` settings and point it at this repository.

## What the bridge converts

- Creates a native `.factory-plugin/plugin.json` for every Cursor marketplace plugin.
- Copies Cursor `agents/` to Factory `droids/`.
- Keeps `skills/`, `commands/`, and `mcp.json`.
- Rewrites `${CURSOR_PLUGIN_ROOT}` references to `${DROID_PLUGIN_ROOT}`.
- Converts Cursor hook events that have a safe Factory equivalent.
- Preserves the original Cursor hook file as `hooks/hooks.cursor.json` when conversion occurs.
- Preserves Cursor-only assets and records known limitations in `droid-marketplace/compatibility.json`.

## Known compatibility boundary

Cursor `rules/`, canvases, and dashboard plugin variables do not have direct Factory Droid plugin equivalents. They are preserved in the mirror but are not falsely treated as native Factory behavior. See the generated compatibility report for per-plugin details.

## Sync

The GitHub Actions workflow `.github/workflows/sync-cursor-droid-marketplace.yml` refreshes the mirror daily and can also be run manually.

Local generation:

```bash
python scripts/sync_cursor_droid_marketplace.py
```

Upstream: https://github.com/cursor/plugins
