#!/usr/bin/env python3
"""Read-only Homelab MCP server for Hermes Agent (stdio JSON-RPC 2.0, zero external deps)."""
import json
import os
import sqlite3
import subprocess
import sys
import urllib.parse
import urllib.request

NOTES_DB = "/home/<TU_USUARIO>/.local/share/homelab-notes/index.sqlite"
VLOGS_URL = "http://192.168.1.97:9428/select/logsql/query"
SSH_KEY = "/home/<TU_USUARIO>/.ssh/proxmox_homelab_ed25519"
URANO_IP = "192.168.1.221"

TOOLS = [
    {
        "name": "search_obsidian_notes",
        "description": "Busca en el indice local FTS5 de notas homelab de Obsidian (solo homelab, nunca work ni secretos).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Terminos de busqueda FTS5"},
                "limit": {"type": "integer", "default": 6}
            },
            "required": ["query"]
        }
    },
    {
        "name": "query_victorialogs",
        "description": "Consulta logs centralizados en VictoriaLogs (VM103 Docker y homelab) usando LogsQL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Consulta LogsQL (ej: '_time:30m error' o '_time:15m container_name:homelab-jellyfin-web-1')"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": ["query"]
        }
    },
    {
        "name": "query_prometheus",
        "description": "Consulta read-only a Prometheus VM103: mode='alerts', 'targets' o 'query' con PromQL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["alerts", "targets", "query"], "default": "alerts"},
                "expr": {"type": "string", "description": "Expresion PromQL (solo si mode='query')"}
            },
            "required": ["mode"]
        }
    },
    {
        "name": "homelab_health_snapshot",
        "description": "Ejecuta health.py en solo lectura para obtener estado en vivo de Proxmox, OPNsense, Traefik CT148, VM103 y HAOS.",
        "inputSchema": {"type": "object", "properties": {}}
    }
]


def tool_search_notes(args):
    q = (args.get("query") or "").strip()
    limit = min(int(args.get("limit") or 6), 15)
    if not q or not os.path.exists(NOTES_DB):
        return {"error": "query vacia o indice FTS5 no encontrado"}
    conn = sqlite3.connect(f"file:{NOTES_DB}?mode=ro", uri=True)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    fts = "notes" if "notes" in tables else next((t for t in tables if "fts" in t.lower()), None)
    if not fts:
        return {"tables": tables, "error": "sin tabla FTS5"}
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({fts})")]
    try:
        rows = conn.execute(f"SELECT * FROM {fts} WHERE {fts} MATCH ? LIMIT ?", (q, limit)).fetchall()
    except sqlite3.OperationalError:
        safe_q = '"' + q.replace('"', '') + '"'
        rows = conn.execute(f"SELECT * FROM {fts} WHERE {fts} MATCH ? LIMIT ?", (safe_q, limit)).fetchall()
    out = []
    for r in rows:
        item = {}
        for c, v in zip(cols, r):
            s = str(v)
            item[c] = s[:400] + ("..." if len(s) > 400 else "")
        out.append(item)
    return {"count": len(out), "results": out}


def tool_vlogs(args):
    q = (args.get("query") or "_time:15m").strip()
    limit = min(int(args.get("limit") or 20), 50)
    data = urllib.parse.urlencode({"query": q, "limit": str(limit)}).encode()
    req = urllib.request.Request(VLOGS_URL, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        lines = r.read().decode("utf-8", "ignore").splitlines()[:limit]
    parsed = []
    for ln in lines:
        try:
            j = json.loads(ln)
            parsed.append({k: j.get(k) for k in ("_time", "host", "container_name", "_msg") if k in j})
        except Exception:
            parsed.append({"raw": ln[:250]})
    return {"count": len(parsed), "logs": parsed}


def tool_prom(args):
    mode = args.get("mode", "alerts")
    if mode == "alerts":
        url = "http://127.0.0.1:19090/api/v1/alerts"
    elif mode == "targets":
        url = "http://127.0.0.1:19090/api/v1/targets"
    else:
        expr = urllib.parse.quote(args.get("expr") or "up")
        url = f"http://127.0.0.1:19090/api/v1/query?query={expr}"
    cmd = [
        "ssh", "-i", SSH_KEY, "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=5", f"root@{URANO_IP}",
        f"qm guest exec 103 -- curl -s '{url}'"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return {"error": r.stderr[:200]}
    qga = json.loads(r.stdout)
    prom = json.loads(qga.get("out-data", "{}"))
    if mode == "targets":
        act = prom.get("data", {}).get("activeTargets", [])
        return {"up": sum(1 for x in act if x["health"] == "up"), "total": len(act), "targets": [(x["labels"].get("job"), x["health"]) for x in act]}
    return prom.get("data", prom)


def tool_health(_args):
    r = subprocess.run(["/usr/bin/python3", "/home/<TU_USUARIO>/.hermes/scripts/health.py"], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return {"error": r.stderr[:300]}
    return json.loads(r.stdout)


def handle(req):
    mid = req.get("id")
    method = req.get("method")
    params = req.get("params") or {}
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "homelab-readonly", "version": "1.0.0"}}}
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if name == "search_obsidian_notes":
                res = tool_search_notes(args)
            elif name == "query_victorialogs":
                res = tool_vlogs(args)
            elif name == "query_prometheus":
                res = tool_prom(args)
            elif name == "homelab_health_snapshot":
                res = tool_health(args)
            else:
                res = {"error": f"unknown tool {name}"}
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)[:12000]}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {"isError": True, "content": [{"type": "text", "text": str(e)}]}}
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found"}}


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        resp = handle(json.loads(line))
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
    except Exception as e:
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}) + "\n")
        sys.stdout.flush()
