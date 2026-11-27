#!/usr/bin/env python3
"""Sync Traefik dynamic routes + wildcard & ACME TLS certs from CT148 (Urano) to CT152 (Jupiter) without ACME conflict."""
import base64, json, os, subprocess

SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "192.168.1.221"]
dyn_raw = subprocess.check_output(SSH + ["pct exec 148 -- cat /opt/traefik/dynamic.json"])
acme_raw = subprocess.check_output(SSH + ["pct exec 148 -- cat /opt/traefik/acme/acme.json"])

dyn = json.loads(dyn_raw)
for r in dyn.get("http", {}).get("routers", {}).values():
    if isinstance(r, dict) and isinstance(r.get("tls"), dict) and "certResolver" in r["tls"]:
        r["tls"] = {}

os.makedirs("/tmp/traefik-sync-certs", exist_ok=True)
certs_out = []
idx = 0

# Pull default wildcard cert (*.<TU_DOMINIO>) from CT148
defc = ((dyn.get("tls") or {}).get("stores") or {}).get("default", {}).get("defaultCertificate")
default_entry = None
if defc:
    cf = defc["certFile"].replace("/etc/traefik/", "/opt/traefik/")
    kf = defc["keyFile"].replace("/etc/traefik/", "/opt/traefik/")
    c_pem = subprocess.check_output(SSH + [f"pct exec 148 -- cat {cf}"])
    k_pem = subprocess.check_output(SSH + [f"pct exec 148 -- cat {kf}"])
    with open("/tmp/traefik-sync-certs/default.crt", "wb") as f: f.write(c_pem)
    with open("/tmp/traefik-sync-certs/default.key", "wb") as f: f.write(k_pem)
    default_entry = {"certFile": "/etc/traefik/certs/default.crt", "keyFile": "/etc/traefik/certs/default.key"}
    certs_out.append(default_entry)

# Pull ACME certs (*.lan.<TU_DOMINIO>)
acme = json.loads(acme_raw)
for resolver_data in acme.values():
    if not isinstance(resolver_data, dict):
        continue
    for c in (resolver_data.get("Certificates") or []):
        with open(f"/tmp/traefik-sync-certs/cert-{idx}.crt", "wb") as f: f.write(base64.b64decode(c["certificate"]))
        with open(f"/tmp/traefik-sync-certs/cert-{idx}.key", "wb") as f: f.write(base64.b64decode(c["key"]))
        certs_out.append({"certFile": f"/etc/traefik/certs/cert-{idx}.crt", "keyFile": f"/etc/traefik/certs/cert-{idx}.key"})
        idx += 1

dyn["tls"] = {"certificates": certs_out}
if default_entry:
    dyn["tls"]["stores"] = {"default": {"defaultCertificate": default_entry}}

with open("/tmp/traefik-sync-dynamic.json", "w") as f:
    json.dump(dyn, f, indent=2)

subprocess.check_call(["pct", "exec", "152", "--", "mkdir", "-p", "/opt/traefik/certs", "/opt/traefik/logs"])
subprocess.check_call(["pct", "push", "152", "/tmp/traefik-sync-dynamic.json", "/opt/traefik/dynamic.json"])
if default_entry:
    subprocess.check_call(["pct", "push", "152", "/tmp/traefik-sync-certs/default.crt", "/opt/traefik/certs/default.crt"])
    subprocess.check_call(["pct", "push", "152", "/tmp/traefik-sync-certs/default.key", "/opt/traefik/certs/default.key", "--perms", "0600"])
for i in range(idx):
    subprocess.check_call(["pct", "push", "152", f"/tmp/traefik-sync-certs/cert-{i}.crt", f"/opt/traefik/certs/cert-{i}.crt"])
    subprocess.check_call(["pct", "push", "152", f"/tmp/traefik-sync-certs/cert-{i}.key", f"/opt/traefik/certs/cert-{i}.key", "--perms", "0600"])

print(f"SYNC_OK: routers={len(dyn.get('http',{}).get('routers',{}))} certs={len(certs_out)}")
