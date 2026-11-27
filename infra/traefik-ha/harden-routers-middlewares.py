#!/usr/bin/env python3
"""Ensure every HTTP router in Traefik dynamic.json applies baseline security-headers and rate-limit."""
import json
import pathlib
import sys

DEFAULT_MWS = [
    "traefik-security-headers--kubernetescrd",
    "traefik-rate-limit--kubernetescrd",
]

def harden(path: pathlib.Path) -> list[str]:
    data = json.loads(path.read_text())
    changed = []
    for name, cfg in data.get("http", {}).get("routers", {}).items():
        if not cfg.get("middlewares"):
            cfg["middlewares"] = list(DEFAULT_MWS)
            changed.append(name)
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n")
    return changed

if __name__ == "__main__":
    target = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/traefik/dynamic.json")
    updated = harden(target)
    print(f"HARDENED: {len(updated)} routers")
