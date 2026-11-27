# Nextcloud application + PostgreSQL — isolated rehearsal, production NOT migrated

## Outcome and limits

Production remains available on Talos: `https://nextcloud.<TU_DOMINIO>`. Application, PostgreSQL and Valkey each retain one Ready replica; pod identities and restart counts are unchanged. Both PVCs remain Bound. HTTPS `/status.php` and `/login`: 200 with validated TLS. No maintenance, routes, replicas, ArgoCD, monitors or autorepair were changed. Nexus was excluded.

The rehearsal restored PostgreSQL and Nextcloud on VM103 with exact image digests, no external network, published ports or schedulers. Verified:

- Transactional PostgreSQL `pg_dump --format=custom --serializable-deferrable`, error-free restore, exact data/sequence fingerprint equality, `pg_amcheck`, and persistence after restarting isolated PostgreSQL.
- Hashes of all copied files, except active Nextcloud logs, before overriding configuration only in the restored copy.
- Nextcloud 35.0.0 installed, maintenance disabled, no DB upgrade required; original user restored without publishing identity.
- Local HTTP `/status.php` and `/login` 200; synthetic user only in the isolated copy, successful WebDAV create/read/delete and user removal.
- Three rehearsal containers stopped/retained, `restart=no`, no OOM. Initial PostgreSQL directory permission failure fixed with UID/GID 70:70; failed container retained stopped.
- Existing non-Nexus VM103 containers retained their IDs, StartedAt and RestartCount.

**The combined capture is NOT an atomic DB/files backup.** File hashes and database data/sequence fingerprints stayed identical throughout the live copy; this demonstrates observed quiescence, not global writer fencing or cross-volume atomic consistency. The PostgreSQL dump itself is transactional. This does not authorize cutover or establish full application rollback. Active logs were excluded from the tar.

The previously accepted synthetic cache rehearsal was not repeated. Ephemeral Valkey was only an application-environment dependency; full production session/locking/cache integration is not claimed. Browser SSO, email, jobs, external integrations and host reboot were not tested.

## Source and storage

Namespace `nextcloud`; deployments `nextcloud`, `nextcloud-db`, `nextcloud-redis`. PVC `nextcloud-html` (10Gi) mounted at `/var/www/html`; PVC `nextcloud-db` (10Gi) at `/var/lib/postgresql`. Both use Longhorn CSI, not direct NFS. Data directory `/var/www/html/data`, approximately 100MiB; complete HTML tree approximately 1.7GiB. The `files_external` application is disabled. No application NFS volume was discovered; VM103 reported no active NFS mounts.

User configuration, credentials, dumps and file contents are not published.

## Capacity and isolation

VM103 and all three inventory hosts (Saturno, Jupiter, Urano) were inspected without changing allocations. VM103 initially had 2,921,759,744 available RAM bytes and 57,193,615,360 free disk bytes. Rehearsal admission required more than 2,300MiB available RAM and 12GiB free disk.

Explicit memory limits: application 768MiB, PostgreSQL 256MiB, Valkey 64MiB; total 1,088MiB, no additional swap, bounded CPU. No RAM expansion or alternate-host deployment. This proves rehearsal fit, **not** production concurrency/capacity sizing.

After the rehearsal, containers stopped: available RAM 2,918,592,512 bytes; free disk 51,783,311,360 bytes, 49% used. Retained remote restore/artifacts occupy 2,779,031,109 bytes under `/var/lib/homelab-nextcloud-rehearsal`; exact images are also retained. Recovery was not deleted to inflate free-capacity reporting.

## Production gates and local patch

Repository `<TU_USUARIO_GIT>/homelab` is **PUBLIC**. Its checkout was not modified; no patch applied, commit made or publication performed there. Only a private reviewable patch exists, validated using `git apply --check`:

`/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/nextcloud-app-db/nextcloud-cutover.UNAPPROVED.patch`

**DO NOT APPLY:** it proposes zero replicas and EndpointSlices for VM103 ports 18111–18113; these ports are not reserved/verified and no production destination is listening. Applying it now would interrupt service. Required gates: specific authorization for public GitOps publication, production configuration/security and resource headroom, an atomically coherent current DB/files capture through controlled maintenance or an equivalent supported mechanism, ready destination, current-data recovery, acceptance and internal/external endpoint checks. This cutover has not started.

## Private evidence

Directory `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/nextcloud-app-db/`: `closure-manifest.json`, `capture.json`, `restore-acceptance.json`, `images.json`, `source-status-final.json`, `https-final.json`, `destination-no-restarts.json`, `capacity-final.txt`, `public-patch-gate.json`. Dumps, tar, hash manifests and private configuration remain only there and in the protected remote copy. Coverage: `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json`; application/DB isolated restore and bounded acceptance recorded, cutover/rollback false; combined application backup NOT verified.
