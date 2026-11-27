# TEI — VM103 production migration

Cutover incident: verification detected stale pod routes after selector removal: legacy Endpoints and controller/mirroring EndpointSlices coexisted. Only stale objects were removed, retaining `tei-vm103`; real DNS/Service and restart tests then passed. A transient failure was observed; uninterrupted availability is not claimed.

**Accepted**. Exact image `ghcr.io/huggingface/text-embeddings-inference@sha256:8de25e75ce39617f17f2f6c77d60a4f75b65e779ed5005420eb1400072a15c1c`; backend `192.168.1.92:18115`, original cluster DNS `tei.mlops.svc.cluster.local:80` retained.

Selected for stateless inference with immutable ~457 MiB model cache and no configured API credentials; measured restore uses 1.37 GiB with ~1 GiB guest available, bounded to 2 GiB/2 CPUs. Other candidates require larger state/dependency/resource work.

Cache hashes match before/after capture and after transfer/restore. Exact-image offline isolated restore produced 384-dimensional embeddings; source/restore/production maximum delta 5.599999999827965e-08. Model is read-only in production with HF_HUB_OFFLINE=1; systemd enabled. Talos replicas 0/no pods; Argo Healthy/Synced at `eb17e09224f4076c4c1d1dc9ce6e3c91320ef5d7` after explicit hard-refresh convergence (initial apply alone was transiently reverted).

Real cluster DNS/service health 200 and embeddings tested before/after systemd restart. Unauthorized LAN rejected by timeout (curl28/HTTP000, not401). Source had no native authentication or public HTTPS endpoint: no fabricated login/TLS test. Network restriction preserved. Host reboot and post-cutover rollback not tested. Retain model archive and previous manifest in `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/tei-production`; recovery must restore source Ready from saved model before routing back and disabling destination; original emptyDir is not durable recovery.

NetAlertX overlay scopes 10.244.5.0 are Kubernetes CNI/Flannel topology; physical LAN scope is 192.168.1.0/24. No scopes/interfaces changed, final retirement design deferred until Kubernetes decommission. Nexus, monitors/autorepair and Kubernetes power state untouched.

Private evidence/capacity: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/tei-production`. Config `bc5713640992598ffcc0154fd2224ddace31f338`, GitOps `eb17e09224f4076c4c1d1dc9ce6e3c91320ef5d7`. Public diff is minimal infrastructure only; evidence/model archive remain private.
