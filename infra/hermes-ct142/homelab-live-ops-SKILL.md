---
name: homelab-live-ops
description: Consultas rápidas en solo lectura del homelab post-Talos (Proxmox, VM103 Docker, Prometheus, OPNsense, Traefik CT148, homelab-ops CT151 y búsqueda local FTS5/Qdrant de notas).
---
# Homelab Live Ops (Post-Talos)

- **Clúster Proxmox:** `jupiter` (.200), `saturno` (.210), `urano` (.221). SSH key `~/.ssh/proxmox_homelab_ed25519` (`IdentitiesOnly=yes`).
- **Plataforma Docker/LXC:** `VM 103` (`192.168.1.92`, Urano) + `CT 146` Immich (.94), `CT 147` Authentik (.95), `CT 148` Traefik (.96, VIP `.240`), `CT 151` homelab-ops (.97, Saturno: Beszel `:8090`, Dozzle `:8080`, VictoriaLogs `:9428`, Wallos `:8282`, Dockge `:5001`, Scrutiny `:8085`, NetAlertX `:20211`).
- **Salud completa JSON:** `python3 /home/<TU_USUARIO>/.hermes/scripts/health.py` (incluye Proxmox, PBS/thin/ZFS, OPNsense CrowdSec/Suricata/updates, Traefik CT148, VM103 Docker y HAOS).
- **Prometheus targets/alertas (en VM103):** `ssh -i ~/.ssh/proxmox_homelab_ed25519 root@192.168.1.221 'qm guest exec 103 -- curl -s http://127.0.0.1:19090/api/v1/alerts'`
- **Búsqueda local de notas homelab (FTS5):** usar scripts en `/home/<TU_USUARIO>/projects/homelab-services-vm103/tools/local-notes/` (nunca indexar `work/` ni secretos).
- **Regla crítica TrueNAS/Urano:** nunca reiniciar `urano` ni `VM 108` sin parar PBS `CT 113` en Saturno y desmontar NFS.
