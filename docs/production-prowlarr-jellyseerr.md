# Production closure: Prowlarr and Jellyseerr

## Accepted

- Prowlarr: original pinned image, cold config copy after GitOps source quiescence; all copied file hashes equal before endpoint adaptation; SQLite integrity/table counts recorded privately. Five authenticated read-only API GETs passed, preserving 9 indexers, 3 applications and 1 indexer proxy. Authenticated Radarr/Sonarr/Lidarr status GETs passed without search/sync commands. Original Service DNS/ClusterIP still works through a dedicated VM103 EndpointSlice. Public HTTPS returns 200.
- Prowlarr quiesce: `327e1345b1b01abc1e223853772682a3a0400cfc`; production cut: `2f5e3c1afa36b037ec43cb3bfb92b1bb327c2b38` in the original homelab GitOps repository. Its ApplicationSet continues to own the original application; this repository owns the restricted backend deployment.
- Jellyseerr production cut: `db10381ab9cebba75a2097778087a1c532f3924d`. Prior authenticated API/dependency acceptance retained. Closure readback confirms HTTPS 200, VM103 ingress, original Deployment desired/actual replicas zero and GitOps Synced/Healthy.
- Both original PVCs and manifests remain available. Neither rollback was exercised.

## Stateful rollback: current data, never the initial snapshot

1. Keep the source GitOps replicas at zero. Stop only the service's dedicated `homelab-<service>.service` on VM103 and confirm its container is stopped.
2. Preserve a new private cold archive of `/var/lib/homelab-<service>`; verify SQLite integrity and inventory/hash the current files. Keep the initial archive separately.
3. Mount the original retained config PVC in a temporary, sole-writer recovery pod on its compatible node. Preserve its old contents separately; replace them with the **current stopped VM103 state**, preserving ownership and verifying file hashes and SQLite integrity. Do not run the original server concurrently.
4. For Prowlarr, reverse only the documented URL adaptations in the restored SQLite Applications/IndexerProxies Settings, using the original private `endpoint-adaptations.private.json`. Preserve credentials, indexers and other current data. For Jellyseerr, retain working public Radarr/Sonarr locations or deliberately restore the original private configuration locations without overwriting current requests/users.
5. Remove the recovery pod before restoring the original application manifest via GitOps. Prowlarr's original pre-quiesce manifest is available at `327e134^:k8s/apps/prowlarr/prowlarr.yaml`; Jellyseerr's at `a1baa28^:k8s/apps/jellyseerr/jellyseerr.yaml`. Restore only that service, not unrelated commits. The original Prowlarr Service selector/targetPort must be restored; remove its VM103-original-service EndpointSlice through its Git owner to avoid dual endpoints.
6. Verify one source writer, public TLS/authenticated status, application state and internal consumer DNS. Keep VM103 stopped. Do not enable the old writer using an outdated archive.

## Blocked next batch

Audiobookshelf, Sonarr, Radarr, Lidarr and Bazarr depend on the same NAS export `/mnt/Datos/Apps/docker`. Read-only client-side mount checks from VM103 fail with **permission denied**, for both NFSv3 and NFSv4. Their sources remain unchanged and running. No NAS/export configuration, unrelated mounts, PBS or hypervisor was changed. Migration of these services requires VM103 to be permitted by the export before any source quiescence; do not work around this by copying the media library locally.

Nexus is excluded. Private evidence/backups/credentials are not included in this repository. Coverage was updated for Jellyseerr and Prowlarr; completion of this batch is not completion of the global migration.
