#!/usr/bin/env bash
set -euo pipefail
docker rm -f homelab-blackbox 2>/dev/null || true
docker run -d --name homelab-blackbox --restart unless-stopped \
  --network homelab-monitoring_default \
  --memory 64m --cpus 0.15 \
  -v /opt/homelab-monitoring/blackbox.yml:/etc/blackbox_exporter/config.yml:ro \
  prom/blackbox-exporter:v0.25.0 \
  --config.file=/etc/blackbox_exporter/config.yml
