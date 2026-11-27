#!/usr/bin/env python3
"""Lightweight journald warning+ shipper to VictoriaLogs (zero external deps)."""
import json, socket, subprocess, time, urllib.request

HOST = socket.gethostname().split(".")[0]
URL = "http://192.168.1.97:9428/insert/jsonline?_stream_fields=host,unit&_msg_field=message&_time_field=timestamp"

def send(batch):
    if not batch:
        return
    body = ("\n".join(batch) + "\n").encode("utf-8", "ignore")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/stream+json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception:
        pass

def main():
    proc = subprocess.Popen(
        ["journalctl", "-f", "-n", "10", "-p", "warning", "-o", "json"],
        stdout=subprocess.PIPE, text=True, bufsize=1
    )
    batch = []
    last = time.time()
    for line in proc.stdout:
        try:
            j = json.loads(line)
            msg = j.get("MESSAGE", "")
            if isinstance(msg, list):
                msg = bytes(msg).decode("utf-8", "ignore")
            ts_us = int(j.get("__REALTIME_TIMESTAMP", int(time.time() * 1e6)))
            rec = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts_us / 1e6)) + f".{ts_us % 1000000:06d}Z",
                "host": f"pve-{HOST}",
                "unit": j.get("_SYSTEMD_UNIT") or j.get("SYSLOG_IDENTIFIER") or "kernel",
                "priority": str(j.get("PRIORITY", "4")),
                "message": str(msg)[:2000],
            }
            batch.append(json.dumps(rec, ensure_ascii=False))
        except Exception:
            continue
        if len(batch) >= 20 or (time.time() - last) >= 5:
            send(batch)
            batch.clear()
            last = time.time()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception:
            time.sleep(5)
