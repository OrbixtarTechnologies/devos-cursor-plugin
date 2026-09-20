#!/usr/bin/env python3
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
import json, shutil, tempfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"droid-marketplace"
URL="https://github.com/cursor/plugins/archive/refs/heads/main.zip"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def rewrite_tree(root):
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md",".mdc",".json",".yaml",".yml",".toml",".txt",".sh",".py",".js",".ts",".tsx"}:
            continue
        try:
            s=p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        s=s.replace("$"+"{CURSOR_PLUGIN_ROOT}","$"+"{DROID_PLUGIN_ROOT}")
        s=s.replace("$CURSOR_PLUGIN_ROOT","$DROID_PLUGIN_ROOT")
        p.write_text(s,encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    archive=td/"cursor.zip"
    with urlopen(URL) as r:
        archive.write_bytes(r.read())
    with ZipFile(archive) as z:
        z.extractall(td)
    upstream=td/"plugins-main"/"plugins"
    mp=load(upstream/".cursor-plugin"/"marketplace.json")
    staging=ROOT/".droid-marketplace-staging"
    if staging.exists():
        shutil.rmtree(staging)
    (staging/"plugins").mkdir(parents=True)
    entries=[]
    compat={"plugins":{}}

    for item in mp.get("plugins",[]):
        name=item.get("name")
        source=item.get("source")
        if not name or not isinstance(source,str):
            continue
        src=upstream/source
        if not src.exists():
            compat["plugins"][name]={"status":"skipped","reason":"source missing"}
            continue
        dst=staging/"plugins"/name
        shutil.copytree(src,dst)
        cm={}
        cpath=dst/".cursor-plugin"/"plugin.json"
        if cpath.exists():
            cm=load(cpath)
        if (dst/"agents").exists() and not (dst/"droids").exists():
            shutil.copytree(dst/"agents",dst/"droids")
        if (dst/".mcp.json").exists() and not (dst/"mcp.json").exists():
            shutil.copy2(dst/".mcp.json",dst/"mcp.json")
        rewrite_tree(dst)
        fm={
            "name":name,
            "description":item.get("description") or cm.get("description") or name,
            "author":cm.get("author") or {"name":"Cursor plugin ecosystem"},
            "x-upstream":{"repository":"cursor/plugins","source":source}
        }
        for k in ("version","homepage","repository","license","keywords"):
            if k in cm:
                fm[k]=cm[k]
        save(dst/".factory-plugin"/"plugin.json",fm)
        entries.append({
            "name":name,
            "description":item.get("description") or fm["description"],
            "source":"./plugins/"+name
        })
        has_rules=(dst/"rules").exists()
        has_hooks=(dst/"hooks").exists()
        compat["plugins"][name]={
            "status":"partial" if has_rules or has_hooks else "full",
            "cursorRules":has_rules,
            "hooksNeedReview":has_hooks
        }

    save(staging/".factory-plugin"/"marketplace.json",{
        "name":"cursor-droid",
        "description":"Cursor plugins adapted for Factory Droid CLI",
        "owner":{"name":"Orbixtar Technologies"},
        "plugins":entries
    })
    save(staging/"compatibility.json",compat)
    (staging/"README.md").write_text(
        "# Cursor to Factory Droid Marketplace\n\n"
        "Generated from https://github.com/cursor/plugins.\n\n"
        "Use the cursor-droid marketplace name. See compatibility.json for partial compatibility notes.\n",
        encoding="utf-8"
    )
    if OUT.exists():
        shutil.rmtree(OUT)
    staging.rename(OUT)
    print("Generated",len(entries),"plugins")
