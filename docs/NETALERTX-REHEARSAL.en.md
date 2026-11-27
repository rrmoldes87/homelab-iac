# NetAlertX — recoverability rehearsal, cutover blocked

Status: **not migrated**. Kubernetes remains healthy and the only writer. No source Deployment, PVC, Service, Ingress, configuration or credentials were changed. Source HTTP and public HTTPS returned 200.

A transactional SQLite backup API snapshot (including WAL), accompanied by configuration files, was restored onto VM103. Local and exact-image offline integrity checks passed, with 17 tables; archive SHA-256 matched after transfer. This is not a cold full-application snapshot or functional acceptance.

Image: `ghcr.io/netalertx/netalertx@sha256:ebce55cdbccc0f71544e6997541fe81db803b8c8bec3079435b8cd0a40d49b7e`.

Real blocker: SCAN_SUBNETS depends on Talos interfaces `cni0` and `flannel.1`, absent from VM103. Only LAN interface `eth0` matches. Removing overlay scans, fabricating interfaces or starting SMTP/SYNC/WORKFLOWS on a changed topology would alter service scope. None was done. The verifier ran SQLite only, with no network and read-only root/data, without scanners or notifications. NET_ADMIN/NET_RAW capabilities were required by the image Python file capabilities even with networking disabled.

No production destination, authenticated acceptance, service persistence test or post-cutover rollback is claimed. Database recoverability is proven; full application backup remains pending. ntfy still lacks a verified consistent memory-cache export; message loss was not accepted.

Final retry capacity before/after: available RAM 2547175424 / 2544099328 bytes; free disk 40132554752 / 40132444160 bytes. Initial image pull preceded this final retry sample. No service or firewall was enabled. Nexus, autorepair and Kubernetes remain unchanged. Headlamp was not selected as a shortcut: it uses an in-cluster identity and retains the Kubernetes API dependency; privileges were not transferred automatically.

Private evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/netalertx-preflight-20261120`. VM103 archive: `/var/lib/homelab-netalertx-rehearsal/snapshot.private.tar`. Never publish archives, device inventory, personal configuration or private evidence. Overlay scanning/notification parity needs explicit redesign before cutover; do not repeat closed migrations.
