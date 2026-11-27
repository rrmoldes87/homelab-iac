#!/usr/bin/env python3
"""Weekly local homelab self-audit (read-only). Notifies ntfy ONLY on failure."""
import datetime, json, os, socket, ssl, subprocess, sys, urllib.request

SSH_KEY = "/home/<TU_USUARIO>/.ssh/proxmox_homelab_ed25519"
NTFY_URL = "http://192.168.1.92:18080/homelab-alerts"
OUT_PATH = "/home/<TU_USUARIO>/.local/share/homelab-audit/last-audit.json"

def ssh(ip, cmd, timeout=15):
    r = subprocess.run(
        ["ssh", "-i", SSH_KEY, "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
         "-o", "ConnectTimeout=5", f"root@{ip}", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:120] or f"rc={r.returncode}")
    return r.stdout.strip()

checks = {}
failures = []

# 1. Traefik HA parity (CT148 MASTER + CT152 BACKUP)
try:
    ov148 = json.loads(ssh("192.168.1.221", "pct exec 148 -- curl -sf http://127.0.0.1:8080/api/overview"))
    ov152 = json.loads(ssh("192.168.1.200", "pct exec 152 -- curl -sf http://127.0.0.1:8080/api/overview"))
    ka148 = ssh("192.168.1.221", "pct exec 148 -- systemctl is-active keepalived")
    ka152 = ssh("192.168.1.200", "pct exec 152 -- systemctl is-active keepalived")
    e148 = ov148["http"]["routers"]["errors"] + ov148["http"]["services"]["errors"]
    e152 = ov152["http"]["routers"]["errors"] + ov152["http"]["services"]["errors"]
    ok = (e148 == 0 and e152 == 0 and ka148 == "active" and ka152 == "active")
    checks["traefik_ha"] = {"ok": ok, "ct148_routers": ov148["http"]["routers"]["total"], "ct152_routers": ov152["http"]["routers"]["total"], "keepalived": [ka148, ka152]}
    if not ok:
        failures.append(f"Traefik HA degradado: e148={e148}, e152={e152}, ka={ka148}/{ka152}")
except Exception as e:
    checks["traefik_ha"] = {"ok": False, "error": str(e)}
    failures.append(f"Traefik HA error: {e}")

# 2. Prometheus targets 100% UP
try:
    raw = json.loads(ssh("192.168.1.221", "qm guest exec 103 -- curl -sf http://127.0.0.1:19090/api/v1/targets"))
    act = json.loads(raw.get("out-data", "{}")).get("data", {}).get("activeTargets", [])
    down = [x["labels"].get("job") for x in act if x.get("health") != "up"]
    ok = (len(act) >= 24 and len(down) == 0)
    checks["prometheus"] = {"ok": ok, "up": len(act) - len(down), "total": len(act), "down": down}
    if not ok:
        failures.append(f"Prometheus targets down: {down}")
except Exception as e:
    checks["prometheus"] = {"ok": False, "error": str(e)}
    failures.append(f"Prometheus error: {e}")

# 3. Scrutiny 5 NVMe SMART PASSED
try:
    sdata = json.loads(urllib.request.urlopen("http://192.168.1.97:8085/api/summary", timeout=8).read())
    devs = sdata.get("data", {}).get("summary", {})
    bad = [f"{v['device'].get('host_id')}:{v['device'].get('device_name')}" for v in devs.values() if v.get("device", {}).get("device_status", 0) != 0]
    ok = (len(devs) >= 5 and len(bad) == 0)
    checks["scrutiny_smart"] = {"ok": ok, "devices": len(devs), "failed": bad}
    if not ok:
        failures.append(f"Scrutiny SMART alerta: devices={len(devs)}, failed={bad}")
except Exception as e:
    checks["scrutiny_smart"] = {"ok": False, "error": str(e)}
    failures.append(f"Scrutiny error: {e}")

# 4. TLS wildcard expiry > 20 days
try:
    ctx = ssl.create_default_context()
    with socket.create_connection(("glance.<TU_DOMINIO>", 443), timeout=5) as sock:
        with ctx.wrap_socket(sock, server_hostname="glance.<TU_DOMINIO>") as ss:
            not_after = ss.getpeercert()["notAfter"]
    exp = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
    days = round((exp - datetime.datetime.now(datetime.timezone.utc)).total_seconds() / 86400, 1)
    ok = days > 20
    checks["tls_wildcard"] = {"ok": ok, "days_remaining": days}
    if not ok:
        failures.append(f"Certificado TLS wildcard caduca en {days} dias")
except Exception as e:
    checks["tls_wildcard"] = {"ok": False, "error": str(e)}
    failures.append(f"TLS check error: {e}")

# 5. VictoriaLogs recent ingestion
try:
    req = urllib.request.Request("http://192.168.1.97:9428/select/logsql/query", data=b"query=_time:30m | stats count() as c", method="POST")
    c = int(json.loads(urllib.request.urlopen(req, timeout=6).read()).get("c", 0))
    ok = c > 0
    checks["victorialogs"] = {"ok": ok, "logs_last_30m": c}
    if not ok:
        failures.append("VictoriaLogs sin ingesta en los ultimos 30m")
except Exception as e:
    checks["victorialogs"] = {"ok": False, "error": str(e)}
    failures.append(f"VictoriaLogs error: {e}")


# 6. Zero firing alerts in Prometheus
try:
    raw_a = json.loads(ssh("192.168.1.221", "qm guest exec 103 -- curl -sf http://127.0.0.1:19090/api/v1/alerts"))
    als = json.loads(raw_a.get("out-data", "{}")).get("data", {}).get("alerts", [])
    firing = [a["labels"].get("alertname") for a in als if a.get("state") == "firing"]
    ok = (len(firing) == 0)
    checks["prometheus_alerts"] = {"ok": ok, "firing_count": len(firing), "firing": firing[:10]}
    if not ok:
        failures.append(f"Alertas firing en Prometheus: {firing[:10]}")
except Exception as e:
    checks["prometheus_alerts"] = {"ok": False, "error": str(e)}
    failures.append(f"Prometheus alerts error: {e}")

report = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "ok" if not failures else "failed",
    "checks": checks,
    "failures": failures,
}
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, ensure_ascii=False))

if failures:
    body = ("Fallo en auditoria semanal homelab:\n- " + "\n- ".join(failures)).encode("utf-8")
    req = urllib.request.Request(NTFY_URL, data=body, headers={"Title": "Homelab Weekly Audit FAILED", "Priority": "4", "Tags": "warning"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass
    sys.exit(1)
