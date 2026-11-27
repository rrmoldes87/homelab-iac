# Forgejo runner: LIMITED operational closure, not full acceptance

The Forgejo application remains accepted. The overall batch and runner compatibility remain INCOMPLETE. This supersedes the runner's old execution-fencing blocker, not previous application acceptance.

## Verified
- Saturno VM117 / talos-worker-3 is stopped, without a QEMU PID, onboot=0; disks retained. Do not reactivate against stale data.
- Identity 33 recovered by offline read-only source-disk inspection and restored on VM103 with UUID/token preserved. Urano backup: `/root/homelab-migration/forgejo-runner/runner-recovery.tar`; SHA256 `34f66cbea58888766fdbf17736a2ecfbf446af50654ff51a87db8a68f3cbccca`.
- Private synthetic jobs 267/268 succeeded, including identity/state persistence after container recreation: https://forgejo.<TU_DOMINIO>/<TU_USUARIO_GIT>/homelab-services-vm103/actions/runs/2 and https://forgejo.<TU_DOMINIO>/<TU_USUARIO_GIT>/homelab-services-vm103/actions/runs/3 . Test branch removed with HTTP404 readback; run evidence retained.
- Temporary admin token revoked, authenticated read rejected with HTTP401 and local token file removed. Legacy registration credential revoked; 35 stale registrations removed, identity 33 retained.
- Source GitOps replicas=0, inert command, no registration secrets. Commit `511edfd389e0814504e1f70da635fbf9bb8e9c33`, exact remote verified, Argo Synced/Healthy at that revision.

## Verified functional extension: internal checkout and isolated build
Runs 270 and 271 succeeded: https://forgejo.<TU_DOMINIO>/<TU_USUARIO_GIT>/homelab-services-vm103/actions/runs/4 and https://forgejo.<TU_DOMINIO>/<TU_USUARIO_GIT>/homelab-services-vm103/actions/runs/5 . Shallow clone of the public internal repository, network-disabled `FROM scratch` build without pulls, synthetic image removed. No external actions, deployments, Kubernetes credentials or real CI. The second acceptance repeated after recreating only the runner container. Temporary branch removed with HTTP404 readback.

Persistent Docker CLI at `/var/lib/homelab-forgejo-runner/docker-cli`, copied offline from the already pinned DinD container. Reproducible offline provisioning with mandatory hash: `compose/forgejo-runner/provision-cli.sh`; test fixture: `tests/fixtures/runner-internal-build.yaml`; sanitized proof: `evidence/forgejo-runner-internal-build.json`. This does NOT enable or accept previous labels, `actions/checkout@v4`, CI dependencies or deployments. Additional job images have not yet been measured or budgeted.

**Observed state change:** a later check finds VM117 in `prelaunch`, `onboot=0`, locked for `backup`; a normal stop request was rejected by that lock, without bypassing it or interrupting the backup. The earlier `stopped` assertion is historical, not current state. Check the backup and reestablish/verify VM117 stopped before expanding runner scope.

## Limits and precise remaining work
### Fencing incident closed: 2026-11-21
The earlier `prelaunch` warning is resolved: VM117 is `stopped`, `qmpstatus=stopped`, with no PID file, QMP socket or QEMU process, and `onboot=0`; no stop was necessary. No historical QMP capture was obtained during backup: the socket is now absent. Logs show the guest was stopped before backup, KVM was started for copying, and stopped afterwards. Installed Proxmox code explicitly uses `paused => 1` for this case, not a guest boot; this is not presented as historical QMP telemetry.

Owner: `root@pam`, task `UPID:saturno:0025347D:01236DBC:6B00FB21:vzdump::root@pam:`, job `backup-c3a4a7f3-a451`, daily 03:00 local to PBS-Truenas. VM117 backup finished at 03:22:19; the aggregate job ended `job errors` because LXC snapshots hit the Saturno thin-pool threshold. Do not conflate the aggregate failure with VM117 backup, or claim a tested restore. No backup, scheduler, storage or monitor was changed.

Safe procedure: preserve `onboot=0`, source GitOps replicas zero and source nft fence; never unlock or force-stop during backup. Identify UPID and query QMP while its socket exists. Scheduled backups may recreate paused KVM for copying without booting Talos; afterwards check stopped state and absence of PID/socket/process. Do not remove backup protection merely to hide this state. nft persistence is provided by the enabled Forgejo service's `ExecStartPre=/usr/bin/python3 /etc/homelab-forgejo/runner-fence.py`.

Destination runner: daemon only, capacity 1 and acceptance-only label; no executing jobs in the observed API queries. Real run 269 remains `waiting`: neither cancelled nor executed. Keep legacy labels disabled. Sanitized proof: `docs/forgejo-runner-evidence/fencing-incident.json`. Twelve-job compatibility remains pending; prioritize a different service next batch instead of further runner expansion here.

Only `vm103-runner-acceptance:host` is enabled: capacity 1, 10m timeout, cache off. Dind has no network, a Unix socket and 512MiB tmpfs; work/tmp are 256MiB/128MiB. Memory limits 768MiB/256MiB, 1 CPU each, logs 2x5MiB per container. Dind is privileged: not suitable for hostile jobs. The runner network reaches Forgejo; absolute egress isolation is NOT claimed.

Previous labels were `ubuntu-latest` (node:20-bookworm), `docker` (docker:dind), `debian-latest` (debian:bookworm), and `self-hosted` (host). Inventory covers default branches of both visible repositories: two CI files, twelve job definitions, all `ubuntu-latest`, using `actions/checkout@v4`. A `.github` file is not evidence of execution on Forgejo. Other branches, invisible repositories and all historic workflows are outside this inventory.

Do NOT enable those labels yet. Remaining gates: pinned offline job images, CI tools/dependencies, storage budget, checkout access and reviewed egress; least-privilege replacement for the previous Kubernetes service-account access; then isolated synthetic tests per profile. Do not run real CI or external-effect jobs as a probe. Never alias `ubuntu-latest` to the host: this changes its environment and could consume queued jobs.

## Recovery and evidence
Secret-free configuration: `compose/forgejo-runner/`; private identity remains outside Git at `/var/lib/homelab-forgejo-runner/.runner` (0600). Unit: `systemd/homelab-forgejo-runner.service`. Keep physical fencing before recovery; do not boot VM117 or register a duplicate identity. Restore identity/configuration, verify hashes and retain the limited profile. Verified backup/restore does NOT establish full post-cutover rollback or VM103 reboot persistence.

Private evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/forgejo-production-20261121/runner-recovery/closure-manifest.json`. All 45 unrelated container IDs/start times remain unchanged. Measured disk: 87%, 13,171,601,408 available bytes; exact data in `closure-health.json`. No expansion or other workload added. Talos mTLS remains unresolved; monitors, Nexus and the rest of Kubernetes were not changed. Public SSH TCP22 is not accepted; previously tested management SSH has a different scope.