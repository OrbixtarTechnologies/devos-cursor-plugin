#!/usr/bin/env python3
"""Generate a Factory Droid marketplace from Cursor's official plugin marketplace."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

UPSTREAM_REPO = "https://github.com/cursor/plugins.git"
UPSTREAM_MARKETPLACE = Path(".cursor-plugin/marketplace.json")
OUTPUT_PLUGINS = Path("droid-marketplace/plugins")
OUTPUT_COMPATIBILITY = Path("droid-marketplace/compatibility.json")
OUTPUT_MARKETPLACE = Path(".factory-plugin/marketplace.json")

TEXT_SUFFIXES = {
    ".md", ".mdc", ".markdown", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".tsx",
    ".jsx", ".ps1", ".bat", ".cmd", ".xml", ".ini", ".cfg",
}

CURSOR_EVENT_MAP: dict[str, tuple[str, str | None, bool]] = {
    "sessionStart": ("SessionStart", None, False),
    "sessionEnd": ("SessionEnd", None, False),
    "preToolUse": ("PreToolUse", None, False),
    "postToolUse": ("PostToolUse", None, False),
    "subagentStop": ("SubagentStop", None, False),
    "preCompact": ("PreCompact", None, False),
    "stop": ("Stop", None, False),
    "beforeSubmitPrompt": ("UserPromptSubmit", None, False),
    "beforeShellExecution": ("PreToolUse", "Execute", True),
    "afterShellExecution": ("PostToolUse", "Execute", True),
    "beforeReadFile": ("PreToolUse", "Read", False),
    "afterFileEdit": ("PostToolUse", "Edit|Create|ApplyPatch", False),
    "beforeMCPExecution": ("PreToolUse", "mcp__.*", False),
    "afterMCPExecution": ("PostToolUse", "mcp__.*", False),
}

FACTORY_NATIVE_EVENTS = {
    "PreToolUse", "PostToolUse", "UserPromptSubmit", "Notification", "Stop",
    "SubagentStop", "PreCompact", "SessionStart", "SessionEnd",
}

TOOL_MATCHER_MAP = {
    "Shell": "Execute",
    "Bash": "Execute",
    "Terminal": "Execute",
    "ReadFile": "Read",
    "WriteFile": "Create|Edit",
    "EditFile": "Edit",
}

BASIC_MANIFEST_FIELDS = (
    "name", "description", "version", "author", "homepage", "repository",
    "license", "keywords",
)


def run(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        list(args), cwd=str(cwd) if cwd else None, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return proc.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_root_variables(text: str) -> str:
    replacements = {
        "${CURSOR_PLUGIN_ROOT}": "${DROID_PLUGIN_ROOT}",
        "$CURSOR_PLUGIN_ROOT": "$DROID_PLUGIN_ROOT",
        "%CURSOR_PLUGIN_ROOT%": "%DROID_PLUGIN_ROOT%",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def transform_text_files(plugin_dir: Path) -> int:
    changed = 0
    for path in plugin_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        updated = normalize_root_variables(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def normalize_hook_command(command: str) -> str:
    command = normalize_root_variables(command)
    command = re.sub(
        r"(?<![A-Za-z0-9_}])\./(?=(?:hooks|scripts|bin|tools)/)",
        "${DROID_PLUGIN_ROOT}/",
        command,
    )
    return command


def map_tool_matcher(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return TOOL_MATCHER_MAP.get(value, value)


def hook_command(entry: dict[str, Any]) -> dict[str, Any] | None:
    raw = entry.get("command")
    if not isinstance(raw, str) or not raw.strip():
        return None
    converted: dict[str, Any] = {
        "type": "command",
        "command": normalize_hook_command(raw),
    }
    timeout = entry.get("timeout")
    if isinstance(timeout, (int, float)) and 0 < timeout <= 600:
        converted["timeout"] = int(timeout)
    return converted


def convert_cursor_hooks(path: Path) -> tuple[list[str], list[str]]:
    if not path.exists():
        return [], []

    try:
        data = load_json(path)
    except Exception as exc:
        backup = path.with_name("hooks.cursor.json")
        path.replace(backup)
        return [], [f"hooks/hooks.json could not be parsed and was preserved as {backup.name}: {exc}"]

    if any(key in FACTORY_NATIVE_EVENTS for key in data.keys()):
        return sorted(key for key in data.keys() if key in FACTORY_NATIVE_EVENTS), []

    cursor_hooks = data.get("hooks")
    if not isinstance(cursor_hooks, dict):
        backup = path.with_name("hooks.cursor.json")
        shutil.copy2(path, backup)
        path.unlink()
        return [], ["Cursor hook configuration was not in the expected {hooks:{...}} format and was disabled for Droid."]

    backup = path.with_name("hooks.cursor.json")
    shutil.copy2(path, backup)

    output: dict[str, list[dict[str, Any]]] = {}
    limitations: list[str] = []
    converted_events: set[str] = set()

    for cursor_event, entries in cursor_hooks.items():
        mapping = CURSOR_EVENT_MAP.get(cursor_event)
        if mapping is None:
            limitations.append(f"Cursor hook event '{cursor_event}' has no safe Factory mapping and is preserved only in hooks.cursor.json.")
            continue
        factory_event, forced_matcher, cursor_matcher_is_command_regex = mapping
        if not isinstance(entries, list):
            limitations.append(f"Cursor hook event '{cursor_event}' was not an array and was skipped.")
            continue

        for entry in entries:
            if not isinstance(entry, dict):
                limitations.append(f"A '{cursor_event}' hook entry was not an object and was skipped.")
                continue
            cmd = hook_command(entry)
            if cmd is None:
                limitations.append(f"A '{cursor_event}' hook without a command was skipped (Factory supports command hooks only).")
                continue

            group: dict[str, Any] = {"hooks": [cmd]}
            cursor_matcher = entry.get("matcher")
            if forced_matcher:
                group["matcher"] = forced_matcher
                if cursor_matcher_is_command_regex and isinstance(cursor_matcher, str) and cursor_matcher:
                    group["commandRegex"] = cursor_matcher
            elif isinstance(cursor_matcher, str) and cursor_matcher:
                group["matcher"] = map_tool_matcher(cursor_matcher)

            output.setdefault(factory_event, []).append(group)
            converted_events.add(cursor_event)

    if output:
        write_json(path, output)
    else:
        path.unlink(missing_ok=True)

    return sorted(converted_events), limitations


def source_manifest(plugin_dir: Path) -> dict[str, Any]:
    candidates = [
        plugin_dir / ".cursor-plugin" / "plugin.json",
        plugin_dir / "plugin.json",
        plugin_dir / ".claude-plugin" / "plugin.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return load_json(candidate)
            except Exception:
                pass
    return {}


def factory_manifest(name: str, entry: dict[str, Any], original: dict[str, Any], source: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    merged = dict(entry)
    merged.update(original)
    for key in BASIC_MANIFEST_FIELDS:
        if key in merged:
            result[key] = merged[key]
    result["name"] = name
    result.setdefault("description", entry.get("description", f"Cursor plugin '{name}' adapted for Factory Droid."))
    result.setdefault("version", original.get("version", "0.0.0-cursor-sync"))
    result.setdefault("author", original.get("author", {"name": "Cursor plugin authors"}))
    result.setdefault("homepage", f"https://github.com/cursor/plugins/tree/main/{source}")
    result.setdefault("repository", "https://github.com/cursor/plugins")
    result["x-cursor-source"] = source
    return result


def plugin_limitations(plugin_dir: Path, original_manifest: dict[str, Any], hook_limitations: list[str]) -> list[str]:
    limitations = list(hook_limitations)
    if (plugin_dir / "rules").exists() or original_manifest.get("rules"):
        limitations.append("Cursor rules are preserved in rules/ but Factory Droid plugins do not currently load Cursor rule files as persistent rules.")
    if original_manifest.get("variables"):
        limitations.append("Cursor dashboard variables are not a Factory plugin feature; configure equivalent environment/MCP values in Factory as required.")
    if original_manifest.get("canvases") or (plugin_dir / "canvases").exists():
        limitations.append("Cursor canvases are preserved but are not a Factory Droid plugin component.")
    return limitations


def convert_plugin(upstream_root: Path, output_root: Path, entry: dict[str, Any]) -> dict[str, Any]:
    name = entry["name"]
    source = entry["source"]
    src = upstream_root / source
    dest = output_root / name
    if not src.is_dir():
        return {"name": name, "source": source, "status": "missing", "limitations": ["Upstream source directory was not found."]}

    shutil.copytree(src, dest, symlinks=False)
    original_manifest = source_manifest(dest)
    write_json(dest / ".factory-plugin" / "plugin.json", factory_manifest(name, entry, original_manifest, source))

    agents = dest / "agents"
    droids = dest / "droids"
    if agents.is_dir() and not droids.exists():
        shutil.copytree(agents, droids)

    if (dest / ".mcp.json").exists() and not (dest / "mcp.json").exists():
        shutil.copy2(dest / ".mcp.json", dest / "mcp.json")

    changed_text_files = transform_text_files(dest)
    converted_hooks, hook_limitations = convert_cursor_hooks(dest / "hooks" / "hooks.json")
    limitations = plugin_limitations(dest, original_manifest, hook_limitations)

    return {
        "name": name,
        "source": source,
        "status": "converted" if not limitations else "converted-with-limitations",
        "transformations": {
            "factoryManifest": True,
            "agentsCopiedToDroids": agents.is_dir(),
            "rootVariableFilesChanged": changed_text_files,
            "cursorHookEventsConverted": converted_hooks,
        },
        "limitations": limitations,
    }


def make_marketplace(upstream_marketplace: dict[str, Any], commit: str) -> dict[str, Any]:
    plugins = []
    for entry in upstream_marketplace.get("plugins", []):
        if not isinstance(entry, dict) or not entry.get("name") or not entry.get("source"):
            continue
        item: dict[str, Any] = {
            "name": entry["name"],
            "description": entry.get("description", "Cursor plugin adapted for Factory Droid."),
            "source": f"./droid-marketplace/plugins/{entry['name']}",
            "homepage": f"https://github.com/cursor/plugins/tree/{commit}/{entry['source']}",
            "tags": ["cursor", "droid", "compatibility-mirror"],
        }
        if "category" in entry:
            item["category"] = entry["category"]
        plugins.append(item)

    return {
        "name": "cursor-droid",
        "description": "Factory Droid-compatible mirror of Cursor's official plugin marketplace.",
        "owner": {"name": "Orbixtar Technologies"},
        "plugins": plugins,
    }


def validate(repo_root: Path, marketplace: dict[str, Any]) -> None:
    names: set[str] = set()
    errors: list[str] = []
    for entry in marketplace.get("plugins", []):
        name = entry.get("name")
        if name in names:
            errors.append(f"duplicate plugin name: {name}")
        names.add(name)
        source = entry.get("source", "")
        if not isinstance(source, str) or not source.startswith("./"):
            errors.append(f"{name}: invalid local source {source!r}")
            continue
        plugin_dir = repo_root / source[2:]
        if not plugin_dir.is_dir():
            errors.append(f"{name}: missing plugin directory {plugin_dir}")
            continue
        manifest = plugin_dir / ".factory-plugin" / "plugin.json"
        if not manifest.exists():
            errors.append(f"{name}: missing {manifest}")
        else:
            try:
                load_json(manifest)
            except Exception as exc:
                errors.append(f"{name}: invalid Factory manifest: {exc}")
    if errors:
        raise SystemExit("Marketplace validation failed:\n- " + "\n- ".join(errors))


def sync(repo_root: Path, upstream_root: Path) -> None:
    upstream_marketplace = load_json(upstream_root / UPSTREAM_MARKETPLACE)
    upstream_commit = run("git", "rev-parse", "HEAD", cwd=upstream_root)

    output_root = repo_root / OUTPUT_PLUGINS
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    compatibility = []
    for entry in upstream_marketplace.get("plugins", []):
        if isinstance(entry, dict) and entry.get("name") and entry.get("source"):
            compatibility.append(convert_plugin(upstream_root, output_root, entry))

    marketplace = make_marketplace(upstream_marketplace, upstream_commit)
    write_json(repo_root / OUTPUT_MARKETPLACE, marketplace)
    write_json(
        repo_root / OUTPUT_COMPATIBILITY,
        {
            "upstream": UPSTREAM_REPO,
            "upstreamCommit": upstream_commit,
            "pluginCount": len(compatibility),
            "plugins": compatibility,
        },
    )
    validate(repo_root, marketplace)
    print(f"Synced {len(compatibility)} Cursor plugins from {upstream_commit}.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root where Factory marketplace files are generated")
    parser.add_argument("--upstream-dir", help="Existing checkout of cursor/plugins; otherwise a shallow clone is created")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if args.upstream_dir:
        sync(repo_root, Path(args.upstream_dir).resolve())
        return

    with tempfile.TemporaryDirectory(prefix="cursor-plugins-") as tmp:
        upstream = Path(tmp) / "plugins"
        run("git", "clone", "--depth", "1", UPSTREAM_REPO, str(upstream))
        sync(repo_root, upstream)


if __name__ == "__main__":
    main()
