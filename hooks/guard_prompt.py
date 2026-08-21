#!/usr/bin/env python3
"""Lightweight prompt guard: emits advisory text only; never blocks user work."""
import json
import sys

def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    prompt = str(payload.get("prompt", payload.get("text", "")))
    risky = any(x in prompt.lower() for x in ["delete database", "drop table", "rm -rf", "rotate production secret", "force push"])
    if risky:
        print(json.dumps({"continue": True, "user_message": "DevOS advisory: this request may be destructive. Require an explicit verification step and prefer dry-run/backups."}))
    else:
        print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
