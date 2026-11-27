# Nextcloud — production accepted on VM103

Date: 2026-11-20. URL: https://nextcloud.<TU_DOMINIO>.

## Outcome and single writer

Nextcloud 35, PostgreSQL 18 and Valkey are running healthy on VM103. Application: `192.168.1.92:18111`; PostgreSQL: `:18112`; cache: `:18113`. All three original Deployments in `nextcloud` have zero replicas; both original PVCs remain Bound and retained. All three internal Service DNS names work through VM103 endpoints. Kubernetes/Talos was not shut down.

Public routing GitOps: `c54f72dcf71894afb5201e938becd3dad66f3a55`. Private concurrency configuration: `6bf864cc7e31622d9b00c8ada15e1d0d81429989`. Publications were checked against the exact remote reference. Images are digest-pinned in `compose/nextcloud/compose.json`; no image upgrades were made.

## Capture, recovery and real acceptance

- Source entered maintenance; application/cache stopped, transactional PostgreSQL dump captured, then DB stopped. File and database copies were captured with writers fenced. This is a jointly consistent offline capture, **not a simultaneous atomic snapshot** across both volumes.
- Files and database restored; file manifests and database data/sequences compared before opening the destination writer; `pg_amcheck` passed again in production. Private dump and physical copies are retained.
- Certificate-validated HTTPS. Anonymous DAV returned 401; an independent synthetic account performed PUT 201, GET 200 with exact content, DELETE 204. No test writes to a real user's account.
- Full application/DB/cache stop/start retained the synthetic file, read successfully before deletion. The synthetic account was deleted and the original user list remained unchanged.
- Native CSRF-protected form login with Origin reached `/apps/dashboard/` with 200. The original test omitted Origin and triggered CSRF/SameSite protection; this was not evidence of incorrect credentials. This is not a full browser SSO test.
- Nextcloud Redis locking configuration and ping verified; ephemeral cache reconstructed after restart. All three internal DNS names checked.
- Three healthy containers without OOM; systemd enabled and active. Identity, start time and restart counts of **59 unrelated containers** unchanged from baseline.

## Exit 137 and resource limits

Urano kernel records identify OOM of `python3` in `/lxc/142/ns/system.slice/hermes-gateway.service`, anonymous RSS 3694796 kB. The recovery helper buffered an entire tar in memory. **This was not an application or VM103 OOM**. That transfer now uses file-backed subprocess input/output instead of whole-archive buffers. Full archive streaming to remote SHA256 and bounded tar download were exercised without writing user data. This does not constitute a complete production rollback test.

Limits: application 1024 MiB/1.25 CPU, DB 384 MiB/0.5 CPU, Valkey 96 MiB/0.25 CPU; each container's memory+swap maximum equals its memory limit. Apache: two workers; PHP: 512M. Cache: 64 MiB, noeviction, no RDB persistence. No RAM expansion or redistribution from other services.

Measured capacity before/after: MemAvailable 3041435648 → 2947358720 bytes; free disk 51796656128 → 46410481664 bytes. Disk reduction includes retained copies/attempts. Observed application/DB/cache memory: 106.1/36.57/3.883 MiB; this is a sample, not a peak guarantee. Required headroom: available RAM >1200 MiB and disk >12 GiB.

## Evidence and remaining limits

Private directory: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/nextcloud-production/`. Reference: `closure-manifest.json`, with evidence and coverage hashes; checks in `production-functional-acceptance.json`, `closure-health.json`, `exit137-diagnosis.json`, `streaming-recovery-helper-validation.json`. Local coverage: `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json`.

Not claimed verified: full VM103 reboot, browser SSO, current-data production rollback, a new periodic external backup. Never overwrite the active writer with an older copy: returning to source requires maintenance, fencing VM103, and consistently transferring **its current data** to retained PVCs. Preserve copies/attempts; do not delete for capacity without another verified recovery path.

## Authorized global final acceptance, still pending

After all migrations/dependencies: balance placement using measured CPU/RAM/disk/load, verify availability, persistence and backups, and only then gracefully shut down Kubernetes/Talos VMs. Shutdown releases CPU/RAM, **not disk**; it does not authorize deleting VMs, disks, PVCs or copies. Nexus remains excluded and must be resolved as a dependency without breaking it before shutdown. This is a documented pending item, not cron or Kanban. No other workload is started during Nextcloud closure.
