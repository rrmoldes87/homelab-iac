# Actual Budget — accepted production migration

Date: 2026-11-20. Production: https://actual.<TU_DOMINIO>. See [the Spanish operational runbook](ACTUAL-BUDGET.es.md) for the complete ordered rollback procedure.

Closure, measured capacity and next candidates: [ES/EN batch report](BATCH-CLOSURE-2026-11-20.es-en.md). The next batch is capacity-gated; no storage expansion or additional migration was performed.

## Running state

- Exact source image, version 26.11.0: `docker.io/actualbudget/actual-server@sha256:06cf186569cf58d93e12659ff1a517b65b5b0ebee7050a3991d4bd8a1d398da6`. No application upgrade.
- Single active writer: dedicated enabled `homelab-actual-budget.service` on VM103, `192.168.1.92:18107`; cluster-only listener firewall. Installed configuration `/etc/homelab-actual-budget`; current data `/var/lib/homelab-actual-budget-v2/data`.
- Original Service name/port, DNS, TLS and Ingress retained. Selectorless `actual-budget:5006` points through `actual-budget-vm103` EndpointSlice to VM103:18107.
- Source Deployment stays at zero, pinned to the exact digest. Original Longhorn PVC `actual-budget-data` retained Bound, UID `6ebfaac6-5011-4e8e-8cdf-a8ddcc4adbea`. It is a stopped snapshot, not current destination data.

## What actually passed

Source application pods were absent before copying the whole cold directory, including SQLite/WAL and budget blobs. Every copied file hash matched before starting the destination. All SQLite integrity checks and table counts matched after startup.

Normal-CA production HTTPS: homepage 200; existing-session authenticated budget inventory unchanged; one existing budget blob downloaded with exactly the source SHA-256; anonymous access rejected 401. Original Service DNS was exercised from a Kubernetes pod. Production authentication and blob download passed again after restarting only the dedicated destination unit. Argo `app-actual-budget` was Synced/Healthy at `fe6030f5d13523892e8fd89e88bf76153d00dbaa`.

All 42 unrelated running containers kept the same ID, StartedAt and restart count. No Docker daemon/host restart, no financial writes or bank synchronization, no browser UI interaction and no host reboot test. Do not claim those untested properties.

## Initial failure and recovery

The first attempt incorrectly required `/info.status=ok`; the real endpoint exposes `build.version`. The service itself was running. Its current stopped state was archived and copied back to the PVC with both writers off; every returned file hash matched. The original route/writer was restored, then HTTPS and authenticated inventory were checked after convergence. The second attempt took a fresh consistent source copy and uses the separate `-v2` data directory. The old `/var/lib/homelab-actual-budget/data` is retained stopped evidence, never a current recovery source.

This exercised current-data return after destination startup but before switching the production route. It was not a rollback test after new financial writes.

## Future rollback: preserve current data

1. Coordinate client downtime; keep the source at zero.
2. Stop only `homelab-actual-budget.service`; verify the destination writer is gone. Never start the stale PVC or use `down -v`.
3. Archive the entire **current** `/var/lib/homelab-actual-budget-v2/data` while stopped, preserving owners/modes. Keep the private archive outside Git.
4. Mount the original PVC in a non-application helper pod on its storage node. Back up its old contents before replacement. With both writers absent, replace the directory from the current destination archive. Archive it back, compare each file hash, and check every SQLite integrity result.
5. Commit only to the authorized `homelab.git`: restore the original Service selector, remove the manual destination EndpointSlice, set Deployment replicas to one with the exact digest. Read back remote SHA; wait for Argo Synced/Healthy, source rollout and endpoints.
6. Check normal-CA HTTPS, existing authenticated inventory and blob download; remove helper. Keep destination stopped. To reapply VM103 later, repeat a fresh cold copy from the now-current source. Never run two writers or reuse an old acceptance archive as current data.

The private migration script exercised the reverse-copy/hash path during the initial incident. Do not rerun completed migration phases blindly. Local snapshots are recovery artifacts, not a claim of automated offsite backups.

## Evidence and commits

Private directory: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/actual-budget-production-attempt2`; use `result.json`, `download-and-restart-acceptance.json`, `cold-copy-verification.private.json`, `sqlite-before.private.json`, `sqlite-after.private.json`, `unrelated-lifecycle.json`. Prior rollback: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/actual-budget-production/rollback-current-verified.json`.

Active configuration `665b3b06d8f3085bdf1a0cf1ebf2239d280f1c5f`; source stop `fc4678481c1ba8495399e23fde23143f49e10696`; production bridge `fe6030f5d13523892e8fd89e88bf76153d00dbaa`.

Evidence includes private financial/account data: never commit or print it. At closure VM103 had 9941 MiB total RAM, 3601 MiB available and 8.4 GiB free disk (82% used). This small service was selected instead of extending the batch to larger multi-component workloads. Nextcloud/DefectDojo/ntfy remain outside this cutover. Nexus, monitoring and autorepair were excluded and untouched.
