# Production close: Bazarr, qBittorrent, MLflow and Qdrant

All four source Deployments are at **0 desired / 0 current replicas**; destination systemd units are active. Owning Argo Applications are `Synced/Healthy`. Original PVCs are retained. Exact running image digests are pinned; no version upgrades. Private copies and acceptance files are intentionally not tracked.

| Service | VM103 listener | Original GitOps cut commit | Read-only acceptance |
|---|---:|---|---|
| Bazarr | 18097 | `99f4c6adc47583ca9e0a72a2d79751983dca0ecc` | HTTPS 200; authenticated API; series/movie identifiers equal; Sonarr/Radarr dependencies on retained HTTPS endpoints |
| qBittorrent | 18098, P2P 6881 TCP/UDP | `71726ff28f605fb1b1c00ed53d62ea742791a2ac` | HTTPS login and version; all 94 torrent hashes equal; save path retained; TCP P2P via original LoadBalancer succeeds |
| MLflow | 18099 | `68446d1192b128b89d7fa989533264d352569fe0` | Cold-copy hashes equal, SQLite integrity OK, existing experiments API equal, production HTTPS 200 |
| Qdrant | 18100 HTTP, 18101 gRPC | `cc1188a0774597d9c6bcb67d2924f73fb0d3034e` | Cold-copy hashes equal; collections inventory equal through original cluster DNS; gRPC TCP handshake through original ClusterIP |

Qdrant remains **internal only**. No public ingress was added. Original Services retain cluster DNS via managed EndpointSlices, including named secondary ports. MLflow/Qdrant share `app-mlops`: do not derive their GitOps owner from individual Deployment names. Existing ingress TLS/middleware policy is preserved, not broadened.

## Rollback boundary

These stateful rollback cycles have **not been exercised**. UDP peer transfer has not been exercised; the UDP listener and EndpointSlice are verified. No notifications, experiments or vector writes were created for acceptance.

Never merely revert the cut commit and start the old PVC. Stop the destination unit first, archive its **current** `/var/lib/homelab-<service>` tree, and return those files to the original PVC using a temporary writable helper, with both app writers stopped. Preserve the old PVC contents separately. Verify the returned file hashes against the current destination archive before restoring the original routing and replica count through the owning GitOps application. If return verification fails, keep both writers stopped and retain all archives; do not revive the stale source. MLflow/Qdrant failure handlers implement this return-and-verify sequence; successful-cut rollback is an explicit operator procedure.

Private operator evidence: `work/homelab-migration/<service>-production/production-acceptance.json`, `current-batch-readback.json`; coverage is maintained outside Git. Bazarr/qBittorrent use the private media migration runner; MLflow/Qdrant use the private MLops runner. These are not secrets/config backups in this repository.

Remaining work is **not complete**. The next batch needs a new live capacity check (last observed: 2,547 MiB available RAM, 20 GiB free disk). ntfy lacks persistent cache/auth files in the source's expected locations and requires a supported preservation plan before stopping it. Jellyfin's source hardware transcode devices have no `/dev/dri` counterpart on VM103. Legacy aria2/netalertx have no Argo tracking owner on their Deployments; discover their authoritative configuration before changing them. Headlamp requires cluster API/auth continuity. Larger multi-component stacks and cluster infrastructure are outside this accepted batch. Financial services remain scope-gated. Nexus is excluded.
