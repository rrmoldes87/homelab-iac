# Jellyfin — VM103 production

Accepted: VM103 is the single writer; original Deployment remains at zero with its Bound PVC retained. Original Service DNS and Ingress remain; an EndpointSlice targets the external backend.

- URL: https://jellyfin.<TU_DOMINIO>
- Backend: 192.168.1.92:18114
- Image: `lscr.io/linuxserver/jellyfin@sha256:b10044530553b2506f06279bf0b5223f9534f434f87a277da4b8fa8ac386cb58`
- Public cutover commit: `6242cf05bfe2d43b9becbde53c5bc7a85487603c`
- Private configuration commit: `402d1b51843128b5f91f1726619e93af67960ae2`
- Evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/jellyfin-production/attempt3/closure-manifest.json`

## Evidence and limits
Source-fenced cold copy, identical file SHA256 values and SQLite integrity_check=ok. Authenticated API returned 1 user and 2 libraries. Logical hash of every original Users row was unchanged; the temporary verification API key was removed before the final clean restart. Internal Service DNS and public HTTPS health passed. No forced scan or external playback. Original-password browser login, playback, transcoding, host reboot and post-acceptance rollback were not tested.

Effective database: /config/data/data/jellyfin.db. Libraries under /config/data and /data/media; UID/GID 1000 read/execute access verified on both sides. /data retains the same rw NFS export 192.168.1.157:/mnt/Datos/Apps/docker. Original hardware acceleration was none with empty /dev/dri; no GPU enabled. Destination limited to 2 GiB / 2 CPUs; listener firewall allows cluster network and local interface only.

## Incidents and recovery
HTTP 000 represented refused connections between initial and final startup listeners, not 401. Readiness now requires stable /health Healthy. Attempt one reverted an over-strict rule excluding the valid /config/data library; attempt two reverted a non-idempotent removal of an already-removed Service selector. Neither is counted as accepted. Original startup then exposed an external mod-download dependency: the preserved exact cache was restored and persisted via a PVC subPath. Healthy original service was verified before the final attempt. Original user credentials were not changed.

## Operations and rollback
Enabled unit homelab-jellyfin.service. Compose /etc/homelab-jellyfin/compose.json; data /var/lib/homelab-jellyfin/config; mod cache /var/lib/homelab-jellyfin/modcache. Cold backups and private evidence retained.
After acceptance, rollback must first fence/stop VM103 and back up CURRENT cleanly closed data. Return current config to the retained PVC using an exclusive helper; verify hashes and integrity. Remove helper and external EndpointSlice, restore Service selector and one original replica with the exact image and persistent mod cache. Publish/read back GitOps and await internal/public Healthy. Never run both writers or restore stale data over newer writes. Final post-acceptance rollback was not rehearsed.

## Capacity
Before:
```text
               total        used        free      shared  buff/cache   available
Mem:     10424713216  6793564160   413773824   550682624  3217375232  2750435328
Swap:              0           0           0
Filesystem       1B-blocks        Used   Available Use% Mounted on
/dev/sda1      99702718464 57459331072 42226610176  58% /
```
After:
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

No Nexus, other-service, monitoring or Kubernetes shutdown changes.
