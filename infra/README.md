# Infraestructura, HA y Observabilidad (`infra/`)

Cada subdirectorio agrupa configuración declarativa, unidades systemd y scripts reproducibles (sin secretos):

- **`traefik-ha/`:** Traefik `CT 148` (MASTER) + `CT 152` (BACKUP) con Keepalived VRRP unicast, sincronización de rutas/TLS cada 5 min y endurecimiento automático de middlewares (`harden-routers-middlewares.py`).
- **`prometheus-vm103/`:** Scrape de 24 targets, Blackbox Exporter (HTTP/TLS/DNS), reglas de alertas SRE, Alertmanager (Telegram + ntfy), 5 dashboards Grafana JSON IaC y datasource nativo VictoriaLogs.
- **`logging-and-smart/`:** Ingesta de logs Docker (Vector) y `journald` (PVE) a VictoriaLogs + timers SMART Scrutiny.
- **`maintenance/`:** Rotación estándar de logs Docker (`docker-daemon.json`), prune semanal, auto-auditoría semanal SRE (`homelab-weekly-audit.py`) y drop-ins de Healthchecks.
- **`authentik-oidc/`:** Script idempotente para crear proveedores OIDC nativos sin secretos en Git.
- **`hermes-ct142/`:** Hardening systemd, remediador autónomo con protección NFS/TrueNAS (`alert_only`) y MCP read-only.
- **`proxmox-backup/` y `proxmox-startup-order/`:** Política de jobs PBS y orden de arranque de invitados Proxmox.
