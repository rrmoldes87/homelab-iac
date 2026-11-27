# DefectDojo — Talos → VM103 production closure

Status: production on VM103, single writer. Closure dated 2026-11-20; DefectDojo only. No additional workload started.

## Destination and durability

- URL: `https://dojo.<TU_DOMINIO>`; existing Authentik web authentication retained.
- Compose project `homelab-defectdojo`; configuration `/etc/homelab-defectdojo/compose.json`, data `/var/lib/homelab-defectdojo`.
- Five services pinned to exact image digests: PostgreSQL, Redis, uwsgi, nginx and worker. Existing secrets and media retained; not published here.
- `homelab-defectdojo.service` enabled and active. Compose uses `restart: unless-stopped`; systemd starts with `up -d --no-recreate` and stops with `stop`, preserving containers and network.
- Installed configuration SHA-256 matches repository files. No container recreation/restart during closure: IDs, StartedAt and RestartCount for **all** containers unchanged before/after. Host reboot not tested.

## Source, GitOps and internal endpoints

Cutover commit in `<TU_USUARIO_GIT>/homelab` (local checkout `homelab-ittools-bridge`): `3954d503a3606c46b82d2dcb660ea6c0301caf70`; ArgoCD `app-defectdojo` Synced/Healthy at that revision.

All four deployments (`dojo-web`, `dojo-celery-worker`, `dojo-db`, `dojo-redis`) have zero desired/actual replicas. No namespace pods remain. Both original PVCs remain Bound; **they are not an up-to-date copy of the destination writer** after cutover.

Existing Service DNS and ports are retained through ready EndpointSlices targeting VM103:

| Service DNS under `defectdojo.svc.cluster.local` | Service port | VM103 |
|---|---:|---:|
| `dojo-web` | 8080 | 192.168.1.92:18108 |
| `dojo-db` | 5432 | 192.168.1.92:18109 |
| `dojo-redis` | 6379 | 192.168.1.92:18110 |

An unprivileged temporary pod using the application's exact image verified internal login **200**, anonymous API **403**, Redis **PONG**, and PostgreSQL SSL negotiation **N** (valid protocol reply, not a TLS claim). Pod deleted. The checker initially used port 80 instead of Service port 8080; **the checker** was corrected, with no endpoint changes. Old empty slices provide no backends. Direct ports 18108–18110 are blocked from the management machine.

## Acceptance and recovery actually tested

- HTTPS TLS validation succeeds; `/login` returns **302 to Authentik**.
- Authenticated read-only API: products, findings and users **200**; anonymous HTTPS request rejected **401**. Temporary probe credential removed; token table empty again.
- Five running containers, zero restarts and no OOM; worker active. Celery control `pong` verified earlier. No synthetic tasks, notifications or jobs sent during this closure.
- Initial consistent restore: PostgreSQL logical dump equals source, media hashes equal, `pg_amcheck` passes, Redis RDB checksum valid, Celery queue empty in initial copy.
- Pending Django migrations required by the existing exact images were applied with web stopped. Final migration check passes; application database amcheck passes. Auxiliary `postgres`/`template1` databases lack the amcheck extension and were skipped by the tool.
- A **post-schema-alignment** PostgreSQL backup was restored in a separate container using the exact image and `network none`; normalized schema equality, core counts and amcheck passed. Checker stopped and retained.
- **Not tested:** full browser SSO login, full application rollback, or host reboot. Isolated PostgreSQL restore **is not** full rollback and does not validate a combined restore of post-cutover media/Redis.

Do not reactivate the source against old PVC data. A real rollback requires first stopping destination writers, backing up/restoring current PostgreSQL/media/Redis, checking schema compatibility, and only then reversing routes/writer. That procedure was not executed and immediate switchback is not claimed.

Inherited warnings observed: default credential-encryption key and `ALLOWED_HOSTS=*`. Left unchanged: rotating the key without handling stored credentials can invalidate them. Hardening is outside this closure.

## Capacity and evidence

Previously completed expansion: disk 48 → 96 GiB, gated by PBS backup and isolated VM104 restore. Root filesystem grew from 49,754,808,896 to 99,702,718,464 bytes; immediately after expansion 58,920,259,584 bytes available, 41% used. DefectDojo closure: 57,193,615,360 bytes available, 43% used; available memory 2,805 MiB. Expansion was not repeated.

Private evidence directory: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/defectdojo-production/`:

- `closure-manifest.json`: absolute paths, SHA-256, commits and remote verification.
- `closure-health.json`, `https-closure.json`, `service-dns-network.json`, `capacity-closure.txt`.
- `restore.json`, `postcutover-restore-proof.json`, `current-pg.dump`, `schema-alignment.private.log`.
- `service-durability.txt`, `durability-no-restarts.json`, `cutover.json`.

Expansion gate evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/vm103-expand-96g/`.
Local coverage: `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json`; all four deployments record verified cutover/backup/restore/bounded acceptance, with full rollback/browser SSO/host reboot explicitly **unverified**. Original `images` fields describe source inventory; exact destination images are in Compose and evidence. Backups, secrets and private evidence are not published to Git.
