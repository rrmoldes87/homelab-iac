# Production batch: Homebox, Gatus and Code-server

All three services use the exact digest observed on the original running Kubernetes pod. No application upgrade, database conversion or binary patch was performed. Private runtime environment/configuration is installed outside this repository. Their original Deployments and PVCs remain present; replicas are zero in the source GitOps repository so self-healing cannot restore a second writer.

| Service | VM103 listener | Production acceptance | Source cutover commit |
|---|---|---|---|
| Homebox | 18088 → 7745 | Original v0.27.1 build and OIDC configuration preserved; cold-copy file hashes and SQLite integrity/table counts equal; public TLS dashboard/status API 200 | `8247429a5e7914f8a50216ac5ff6b290d7ff37bf` |
| Gatus | 18089 → 8080 | Original binary and private monitor config; cold-copy hashes equal, SQLite integrity OK; TLS dashboard 200 and API retains the same 40 endpoint keys | `8a36ed5088fb4475d7205d89075d01b37154d25a` |
| Code-server | 18090 → 8443 | 44 cold-copied files have identical hashes; three SQLite stores pass integrity; health and workbench return 200 with original workspace redirect; public TLS retains Authentik SSO redirect | `d0e64ae8d53bf989102a96e45c8d3711fe43b566` |

These are basic production checks, not authenticated UI/CRUD or editing tests. Rollback was not exercised. A public SSO redirect proves the access boundary is present, not that an authenticated browser session has been exercised. Evidence, database row counts, file inventories and archives are private and not committed.

## Current-state rollback: preserve the old PVC, never resume stale data

After the destination has started, **do not revert the quiesce commit and start the original PVC**. Background jobs can write state even before ingress switches. The cold source archive is a historical backup, not a current rollback source.

Perform rollback for one service at a time:

1. Record the current Git revisions, live Ingress backend, zero source replicas and destination container identity. Keep originals and historical backups untouched.
2. Stop its systemd unit on VM103 (`sudo systemctl stop homelab-SERVICE.service`) and confirm no container for that Compose project remains running. The source must still have zero replicas. Maintain both writers stopped until current-state transfer is verified.
3. Create a new private output directory with mode 0700, then stream `sudo tar cpf - -C /var/lib/homelab-SERVICE .` over SSH into a mode-0600 archive. Compute SHA-256 of the archive and every regular member; check SQLite integrity, copying any WAL/SHM sidecars along with their database. Capture the stopped current directory, **not** an old archive. Keep the VM103 current directory untouched.
4. Provision a **new** rollback PVC in the original namespace, using the original StorageClass/access mode and capacity at least as large as current measured data. Keep the original PVC unmodified. Use a temporary helper with an approved shell/tar-capable image and the new PVC mounted read-write. Restore the complete archive with owners, permissions and links preserved. Compare every restored file hash and relevant SQLite integrity/table counts before starting any application pod. Do not restore into the old PVC or leave old-only files mixed with current state.
5. Commit the source Deployment volume claim change to that new, verified rollback PVC and set replicas to one in the owning source GitOps repository. Leave the Ingress pointing at VM103 until the restored source passes direct health/API and configuration checks. The VM103 systemd unit must remain stopped throughout.
6. Commit the Ingress backend back to the original Kubernetes Service. Wait for the owning Application to be Synced/Healthy at the new revision, read back the exact backend and endpoint, and repeat public TLS/access-boundary and functional checks. Re-enable neither VM103 nor any old source PVC as a writer.
7. Retain the original PVC, the VM103 directory and both old/current private archives. Keep the VM103 unit disabled after confirmed rollback. Update coverage with actual acceptance results; do not mark rollback verified merely because this procedure exists.

If source restart or public validation fails, stop that new source writer before returning the latest state to VM103. The same single-writer/current-state-transfer rule applies in both directions.

## Follow-on work

Authenticated Homebox CRUD/import-export, an authenticated Code-server editing/WebSocket session, and a rollback exercise remain unverified. Audiobookshelf requires explicit handling of its separate configuration, metadata and NFS media volumes; this batch does not claim it migrated. Nexus is excluded.
