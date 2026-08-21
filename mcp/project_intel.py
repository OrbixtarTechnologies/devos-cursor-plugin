#!/usr/bin/env python3
"""Minimal stdio MCP server for safe repository intelligence.

No writes, network access, secret extraction, or arbitrary shell execution
are exposed. Git status is the only subprocess and is read-only.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


_ENV_ROOT = os.environ.get("DEVOS_PROJECT_ROOT")
if _ENV_ROOT:
    ROOT = Path(_ENV_ROOT).resolve()
else:
    _cwd = Path.cwd().resolve()
    # Never scan filesystem root; Cursor supplies DEVOS_PROJECT_ROOT in plugin use.
    if _cwd == Path('/'):
        ROOT = Path.home().resolve()
    else:
        ROOT = _cwd
IGNORE_DIRS = {".git", "node_modules", ".next", "dist", "build", "coverage", ".venv", "venv", "__pycache__", ".turbo", ".cache"}


def safe_path(rel: str) -> Path:
    p = (ROOT / rel).resolve()
    if ROOT != p and ROOT not in p.parents:
        raise ValueError("Path escapes project root")
    return p


def list_tree(max_entries=300):
    out=[]
    for p in ROOT.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        rel=p.relative_to(ROOT)
        out.append(str(rel) + ("/" if p.is_dir() else ""))
        if len(out) >= max_entries: break
    return sorted(out)


def search_files(pattern: str, max_results=50):
    needle = pattern.lower()
    results=[]
    for p in ROOT.rglob("*"):
        if not p.is_file() or any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.stat().st_size > 2_000_000:
            continue
        try:
            text=p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines=text.splitlines()
        for i,line in enumerate(lines,1):
            if needle in line.lower():
                results.append({"file":str(p.relative_to(ROOT)),"line":i,"text":line[:300]})
                if len(results)>=max_results: return results
    return results


def package_metadata():
    names=["package.json","pyproject.toml","Cargo.toml","go.mod","pom.xml","build.gradle","composer.json","Gemfile"]
    result={}
    for name in names:
        p=ROOT/name
        if p.exists() and p.is_file():
            try:
                txt=p.read_text(encoding="utf-8",errors="ignore")
                result[name]=txt[:12000]
            except Exception: pass
    return result



def devos_memory():
    base=ROOT/'.devos'
    files=['project.md','architecture.md','decisions.md','worklog.md']
    out={}
    if base.exists():
        for name in files:
            p=base/name
            if p.exists() and p.is_file():
                out[name]=p.read_text(encoding='utf-8',errors='replace')[:20000]
    return out

def architecture_signals():
    files=list_tree(1200)
    return {
        'entrypoint_candidates':[x for x in files if any(k in x.lower() for k in ['main.','index.','app.','server.','src/'])][:100],
        'service_candidates':[x for x in files if any(k in x.lower() for k in ['service','api','worker','controller','handler'])][:100],
        'config_candidates':[x for x in files if any(k in x.lower() for k in ['config','docker','compose','terraform','workflow'])][:100],
        'integration_candidates':[x for x in files if any(k in x.lower() for k in ['github','linear','sentry','vercel','stripe','supabase','firebase'])][:100]
    }

def git_status():
    try:
        cp=subprocess.run(["git","status","--short","--branch"],cwd=ROOT,text=True,capture_output=True,timeout=5)
        return {"ok":cp.returncode==0,"output":cp.stdout[:12000],"error":cp.stderr[:4000]}
    except Exception as e:
        return {"ok":False,"error":str(e)}


def discover_tests():
    names=[]
    patterns=("test_*","*_test.py","*.spec.ts","*.test.ts","*.spec.tsx","*.test.tsx","*.spec.js","*.test.js")
    for p in ROOT.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.parts): continue
        if p.is_file() and any(p.match(x) for x in patterns):
            names.append(str(p.relative_to(ROOT)))
            if len(names)>=300: break
    return sorted(names)

TOOLS={
 "repo_tree":{"description":"List relevant repository paths without descending into common build/dependency caches.","inputSchema":{"type":"object","properties":{"max_entries":{"type":"integer","minimum":1,"maximum":1000}},"additionalProperties":False}},
 "search_code":{"description":"Search text in project files for a string and return matching file/line evidence.","inputSchema":{"type":"object","properties":{"pattern":{"type":"string"},"max_results":{"type":"integer","minimum":1,"maximum":200}},"required":["pattern"],"additionalProperties":False}},
 "read_file":{"description":"Read a UTF-8 text file inside the project root, capped for safety.","inputSchema":{"type":"object","properties":{"path":{"type":"string"},"start_line":{"type":"integer","minimum":1},"end_line":{"type":"integer","minimum":1}},"required":["path"],"additionalProperties":False}},
 "project_metadata":{"description":"Inspect common package/build manifest files without executing project code.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
 "git_status":{"description":"Read current Git branch/status. Does not mutate the repository.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
 "discover_tests":{"description":"Find likely unit/integration/e2e test files using common naming conventions.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
 "devos_memory":{"description":"Read non-secret persistent DevOS project memory files when present.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}},
 "architecture_signals":{"description":"Extract lightweight architecture signals from repository paths without executing code.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}}
}

def result(obj):
    return {"content":[{"type":"text","text":json.dumps(obj,ensure_ascii=False,indent=2)}]}

def handle(msg):
    method=msg.get("method")
    params=msg.get("params") or {}
    if method=="initialize":
        return {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"devos-project-intel","version":"2.1.0"}}
    if method=="tools/list":
        return {"tools":[{"name":k,**v} for k,v in TOOLS.items()]}
    if method=="tools/call":
        name=params.get("name"); a=params.get("arguments") or {}
        if name=="repo_tree": return result(list_tree(int(a.get("max_entries",300))))
        if name=="search_code": return result(search_files(str(a.get("pattern","")),int(a.get("max_results",50))))
        if name=="read_file":
            p=safe_path(str(a["path"]))
            if not p.is_file(): raise FileNotFoundError(str(a["path"]))
            text=p.read_text(encoding="utf-8",errors="replace")
            lines=text.splitlines()
            s=max(1,int(a.get("start_line",1))); e=min(len(lines),int(a.get("end_line",s+399)))
            return result({"path":str(p.relative_to(ROOT)),"start_line":s,"end_line":e,"text":"\n".join(lines[s-1:e])})
        if name=="project_metadata": return result(package_metadata())
        if name=="git_status": return result(git_status())
        if name=="discover_tests": return result(discover_tests())
        if name=="devos_memory": return result(devos_memory())
        if name=="architecture_signals": return result(architecture_signals())
        raise ValueError(f"Unknown tool: {name}")
    return None

def main():
    for raw in sys.stdin:
        try:
            msg=json.loads(raw)
            if msg.get("method","").startswith("notifications/"):
                continue
            out=handle(msg)
            if out is not None and "id" in msg:
                print(json.dumps({"jsonrpc":"2.0","id":msg["id"],"result":out}),flush=True)
        except Exception as e:
            if 'msg' in locals() and "id" in msg:
                print(json.dumps({"jsonrpc":"2.0","id":msg["id"],"error":{"code":-32000,"message":str(e)}}),flush=True)

if __name__=="__main__": main()
