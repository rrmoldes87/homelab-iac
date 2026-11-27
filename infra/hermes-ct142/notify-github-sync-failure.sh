#!/usr/bin/env bash
set -euo pipefail
[ -r /root/.config/homelab-github-sync/ntfy.env ] || exit 0
# shellcheck disable=SC1091
. /root/.config/homelab-github-sync/ntfy.env
LOG=$(journalctl -u homelab-github-sync.service -n 8 --no-pager -o cat 2>/dev/null | tail -c 600 || true)
curl -fsS -m 5 \
  -H "Authorization: Bearer ${NTFY_TOKEN}" \
  -H "Title: Fallo en homelab-github-sync (CT 142)" \
  -H "Priority: high" \
  -H "Tags: warning,git" \
  -d "homelab-github-sync.service falló (revisar posible fuga bloqueada o error de red):
${LOG}" \
  "${NTFY_URL}" >/dev/null
