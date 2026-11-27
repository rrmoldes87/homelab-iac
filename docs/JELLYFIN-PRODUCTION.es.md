# Jellyfin — producción VM103

Aceptado: escritor único VM103; Deployment original a cero, PVC Bound conservado. Service DNS e Ingress originales permanecen; EndpointSlice apunta al backend externo.

- URL: https://jellyfin.<TU_DOMINIO>
- Backend: 192.168.1.92:18114
- Image: `lscr.io/linuxserver/jellyfin@sha256:b10044530553b2506f06279bf0b5223f9534f434f87a277da4b8fa8ac386cb58`
- Public cutover commit: `6242cf05bfe2d43b9becbde53c5bc7a85487603c`
- Private configuration commit: `402d1b51843128b5f91f1726619e93af67960ae2`
- Evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/jellyfin-production/attempt3/closure-manifest.json`

## Pruebas y límites
Copia fría con origen cercado; archivos SHA256 idénticos, SQLite integrity_check=ok. API autenticada: 1 usuario y 2 bibliotecas; filas originales de Users idénticas por hash lógico. La clave temporal de verificación se eliminó antes del reinicio limpio final. Salud interna por DNS y HTTPS pública verificadas. Sin escaneo forzado ni reproducción externa. No se verificaron contraseña original en navegador, reproducción, transcodificación, reboot del host ni rollback posterior a aceptación.

Datos efectivos: /config/data/data/jellyfin.db. Bibliotecas en /config/data y /data/media; acceso UID/GID 1000 comprobado en ambos extremos. /data conserva NFS 192.168.1.157:/mnt/Datos/Apps/docker con mismo alcance rw. Aceleración origen none, /dev/dri vacío; no se habilitó GPU. Límite destino 2 GiB y 2 CPU; firewall restringe el listener a red del clúster e interfaz local.

## Incidencias y recuperación
HTTP 000 fue conexión rechazada entre servidor inicial y servidor final, no 401; readiness usa /health Healthy estable. Primer intento revertido por criterio demasiado estricto que excluía la biblioteca /config/data; segundo por eliminar dos veces un selector ya retirado por apply. Ambos preceden a aceptación; no se contabilizan como éxito. Se recuperó el origen. Su arranque dependía de descargar un mod: se restauró la caché exacta conservada y se montó como subPath persistente; recuperación saludable verificada antes del intento final. No se cambiaron credenciales originales.

## Operación y rollback
Unidad homelab-jellyfin.service habilitada. Compose en /etc/homelab-jellyfin/compose.json; datos /var/lib/homelab-jellyfin/config; modcache /var/lib/homelab-jellyfin/modcache. Conservados backups fríos y evidencias privadas.
Para revertir después de aceptación: primero detener/fencear VM103, capturar config ACTUAL tras cierre limpio, verificar backup y devolver datos actuales al PVC mediante helper exclusivo; comprobar hashes e integridad, retirar helper y EndpointSlice externo, reponer selector Service y una réplica con digest exacto y caché de mod persistente. Publicar/verificar GitOps y esperar /health Healthy interno y HTTPS. Nunca levantar ambos escritores ni volver al backup antiguo tras nuevas escrituras. Rollback final no ensayado.

## Capacidad
Antes:
```text
               total        used        free      shared  buff/cache   available
Mem:     10424713216  6793564160   413773824   550682624  3217375232  2750435328
Swap:              0           0           0
Filesystem       1B-blocks        Used   Available Use% Mounted on
/dev/sda1      99702718464 57459331072 42226610176  58% /
```
Después:
```text
               total        used        free      shared  buff/cache   available
Mem:     10424713216  6924959744   211775488   608133120  3287977984  2561470464
Swap:              0           0           0
Filesystem       1B-blocks        Used   Available Use% Mounted on
/dev/sda1      99702718464 59000393728 40685547520  60% /
homelab-jellyfin-web-1 259.3MiB / 2GiB
homelab-nextcloud-app-1 111.6MiB / 1GiB
homelab-nextcloud-db-1 44.62MiB / 384MiB
homelab-nextcloud-redis-1 8.461MiB / 96MiB
homelab-defectdojo-worker-1 182.1MiB / 640MiB
homelab-defectdojo-nginx-1 3.461MiB / 128MiB
homelab-defectdojo-uwsgi-1 316.1MiB / 896MiB
homelab-defectdojo-db-1 58.27MiB / 384MiB
homelab-defectdojo-redis-1 6.469MiB / 128MiB
homelab-actual-budget-web-1 63MiB / 384MiB
homelab-dtrack-backend-api-1 454.3MiB / 1.5GiB
homelab-dtrack-backend-db-1 196.3MiB / 512MiB
homelab-prowlarr-web-1 161.2MiB / 512MiB
homelab-aria2-ariang-1 208KiB / 128MiB
homelab-aria2-rpc-proxy-1 13.48MiB / 128MiB
homelab-stirling-pdf-web-1 672.6MiB / 2GiB
homelab-aria2-aria2-1 3.566MiB / 512MiB
homelab-litellm-web-1 545.1MiB / 2GiB
homelab-qbittorrent-web-1 37.27MiB / 1GiB
homelab-qdrant-web-1 16.4MiB / 1GiB
homelab-dtrack-frontend-web-1 3.832MiB / 256MiB
homelab-flaresolverr-solver-1 114.4MiB / 512MiB
homelab-code-server-web-1 65.89MiB / 1GiB
homelab-radarr-web-1 162.4MiB / 512MiB
homelab-ittools-listener-web-1 4.328MiB / 128MiB
homelab-mealie-web-1 258MiB / 768MiB
homelab-romifleur-web-1 10.57MiB / 128MiB
homelab-audiobookshelf-web-1 50.85MiB / 512MiB
homelab-lidarr-web-1 132.1MiB / 512MiB
homelab-bazarr-web-1 187.4MiB / 512MiB
homelab-searxng-web-1 108.3MiB / 512MiB
homelab-gatus-web-1 22.82MiB / 256MiB
homelab-homebox-web-1 22.43MiB / 256MiB
homelab-searxng-cache-1 5.797MiB / 192MiB
homelab-sonarr-web-1 179.9MiB / 512MiB
homelab-mlflow-web-1 569.5MiB / 1GiB
homelab-jellyseerr-web-1 241MiB / 512MiB
migration-homebox-data-web-1 16.2MiB / 192MiB
migration-mealie-data-web-1 213.5MiB / 384MiB
migration-romifleur-persistent-web-1 14.43MiB / 128MiB
migration-romifleur-dynamic-web-1 11.54MiB / 128MiB
migration-romifleur-web-1 12.21MiB / 128MiB
migration-stateless-flaresolverr-1 48.31MiB / 512MiB
migration-stateless-dtrack-frontend-1 3.375MiB / 256MiB
migration-authentik-clean-20261119t003014z-server-1 656.9MiB / 1.125GiB
migration-authentik-clean-20261119t003014z-postgresql-1 96.17MiB / 384MiB
migration-it-tools-20261119t002215z-web-1 2.977MiB / 128MiB
migration-it-tools-20261119t001306z-web-1 6.641MiB / 128MiB
migration-it-tools-20261119t000947z-web-1 6.992MiB / 128MiB
migration-authentik-server-1 643.3MiB / 2GiB
migration-authentik-postgresql-1 72.23MiB / 768MiB
migration-core-traefik-1 90.98MiB / 9.709GiB
```

Nexus, otros servicios, monitores y apagado Kubernetes fuera de alcance.
