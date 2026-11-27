# Stacks Docker Compose (`compose/`)

Definiciones declarativas de los contenedores desplegados en el homelab:

- **`homelab-ops/` (`CT 151`):** VictoriaLogs, Dozzle, Beszel, Dockge, Scrutiny, NetAlertX, Wallos, Paperless-AI, Diun y Healthchecks.
  - Copiar `healthchecks.env.tmpl` a `/etc/homelab-ops/healthchecks.env` (`chmod 0600`) rellenando `<SECRET_KEY_DJANGO_32_BYTES_HEX>` y `<TU_EMAIL_ADMIN>`.
- **`homelab-apps/` (`CT 154`):** Speedtest Tracker, PairDrop, Pingvin Share, Kavita, LubeLogger, Excalidraw, Jackett y Dozzle Agent.
  - Copiar `speedtest.env.tmpl` a `/etc/homelab-apps/speedtest.env` (`chmod 0600`) rellenando `<APP_KEY_32_BYTES_BASE64>`.
- **`jellyfin-saturno/` (`CT 153`):** Jellyfin con transcodificación hardware VAAPI (`/dev/dri/renderD128`) y montaje NFS `ro,soft` desde TrueNAS.
- **`renovate/`:** Reglas de actualización controlada (`automerge: false`, sin saltos *major* automáticos).
- **Servicios `VM 103` (`compose-core`):** Forgejo, Nextcloud, Gatus, Actual Budget, Homebox, Mealie, SearXNG, Stirling-PDF, Qdrant, *arr stack (Sonarr, Radarr, Lidarr, Bazarr, Prowlarr, Jellyseerr, qBittorrent, FlareSolverr), etc.
