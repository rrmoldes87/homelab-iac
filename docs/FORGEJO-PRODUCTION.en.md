# Forgejo — VM103 production / 2026-11-21

> Subsequent runner status: **LIMITED, not fully accepted**. Execution fencing is now verified; see [runner closure and remaining gates](FORGEJO-RUNNER-LIMITED.en.md). Earlier fencing blockers below are historical.

**Application accepted; combined batch remains blocked by runner execution fencing.** https://forgejo.<TU_DOMINIO>; exact image `code.forgejo.org/forgejo/forgejo@sha256:cc2d74fb4c30385a8ee34de8c8f83344f7316cec70bd2cc7eb82b2802fa28e0b`. VM103 is the sole application writer, HTTP 18116 / restricted SSH 18117. Compose/systemd and owned nft ACL/fence are durable; application secrets remain outside Git.

Cold-copy integrity, isolated exact-image offline restore and authenticated identity 2 were exercised. Final backup retained on Urano `/root/forgejo-migration-20261121/source-final-attempt3.private.tar`, SHA256 read back. Original PVC remains Bound and source Deployment is durably zero in public GitOps. Read-only production SQLite integrity is ok.

Real acceptance: trusted-CA authenticated HTTPS API; private/public Git HTTPS reads; clean app-only systemd restart; published commits, repository identities and host key survive. Other container lifecycles unchanged. No host reboot claim and no uninterrupted-availability claim: earlier cutover attempts required two source recoveries, the last using current destination data.

Private Git SSH authentication passed using a temporary read-only user key, then deletion was read back. Strict RSA host key matches the final source backup. Path uses the existing VM103 management jump to its restricted 18117 listener. **Public DNS TCP22 did not answer**; this is not public SSH acceptance and no new network exposure was added. Existing internal Service names and ingress retained. TLS/DNS still depend on Kubernetes. Public, reviewed infrastructure-only routes and retained-writer fence are Argo Synced/Healthy at `345d89ce008c0217b0f0d85d6261cc1822884877`.

## Separate runner blocker
Worker3 192.168.1.206 (old pod 10.244.5.249) remains Unknown. Bounded kubectl/talosctl diagnostics failed Talos mTLS (unknown authority / incompatible key usage), direct and via control plane. No Talos SSH or shutdown. Unknown, replicas zero, and Terminating do not establish that jobs stopped.

An automatic replacement on worker1 was discovered and paused durably at zero, public commit `8c7ffb19fbb565446b4d12dfef32b0872d1d3a1b`. No active replacement remains; old worker3 pod is retained Terminating. Run 263 is cancelled. Owned atomic nft table at forward priority -10 denies the old worker and pod access to Forgejo listeners, including established flows. This is **server network fencing only, not execution fencing** for already-running jobs targeting other systems. Runner credentials were not moved and no new runner was registered. Resume only with verified node/job execution fencing and a consistent credential backup; obtain valid Talos PKI/operational control rather than force-deleting a pod and assuming its processes died.

## Recovery and capacity limits
Retain original PVC, final external backup, rehearsal gzip, isolated restore and current production data. Never activate a stale origin. Stop destination, back up and transfer its current data to source, validate integrity/auth, then switch routes.

Capacity was already closed at `3c1f2facf5f84a998e2cff4aad097273632a94a9`: disk 96 GiB/EXT4, RAM 14 GiB; no repeated resize. Root before Forgejo: 38,383,042,560 bytes free / 62%; after: 13,677,203,456 bytes free / 87%, including deliberately retained restore/archive copies. Measured available RAM 7,204,962,304 bytes. VM103 onboot remains zero due to unresolved NFS readiness; enabled app service does not remove that limitation. No other workload started, no host shutdown, no Nexus/monitor/autorepair changes.

Private evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/forgejo-production-20261121/closure-manifest.json`. See application/SSH acceptance, key cleanup, Argo readback, configuration hashes, Talos diagnostics, runner network fence and before/after capacity alongside it. Coverage records application acceptance separately from the blocked runner; **combined batch not complete**.
