# Saturno thin-pool exhaustion — partial mitigation, incident open

This is not an accepted migration. The next Vault/ntfy batch is blocked by demonstrated storage risk.

## Executed mitigation

Measured LV/VG capacity, device-mapper state, health, effective autoextend and backup/kernel logs before changing anything. `pve/data` was 100% full; metadata was not exhausted. Saved `vgcfgbackup` at `/root/homelab-migration/saturno-thinpool-20261121/pve-before.conf` (metadata only, NOT a data backup).

Added **8 GiB from the existing VG**, without expanding Urano/VM103 or deleting backups/disks. Final pool: 160230801408 bytes, data **94.64%**, metadata **4.40%**, VG reserve **8594128896 bytes**. Device-mapper reports `rw` without `needs_check`; this does NOT certify guest filesystems. Effective autoextend is threshold 80%, growth 20%; remaining VG space cannot fund that growth. Neither that protection nor the backup schedule was changed.

## Exact impact

Scheduled snapshot backups failed for CT **101,109,111,122,131,140,141,143,145**, reporting `Cannot create new thin volume, free space in thin pool pve/data reached threshold.` VM117 and VM120 backups completed.

One-byte private-file write plus fsync probes confirmed CT111 `vaultwarden` and CT140 `syncthing` are read-only; CT141 `obsidian-web` reports ENOSPC, root 100%, zero available bytes. CT111 systemd remains active despite read-only storage; it is NOT the Kubernetes `vault` deployment. CT101,109,113,122,131,143,145 passed this filesystem probe, not full application acceptance. Probe files were removed.

## Recovery boundaries

PBS-Truenas is active with free space. The newest inventoried backups for CT111/140/141 date from **November 18**; no restore was tested. An additional CT111/140 snapshot attempt under durable systemd unit `homelab-saturno-emergency-backup-20261121.service` failed at the same threshold. It explicitly used `--remove 0 --prune-backups keep-all=1`; no backups were pruned/deleted.

No forced rw remount, mounted-filesystem fsck or service stop was performed. Independent current-data copies, measured reservation, isolated restore and validation are prerequisites to offline repair. Do not blindly consume remaining VG extents. Pool growth alone does not grow CT141's filesystem.

VM103 remains 87% used with 13120339968 bytes available and received no new volumes. VM117 remains stopped; run269 remains waiting and was not launched. Nexus, remaining Kubernetes, TrueNAS, monitoring and backup scheduling were untouched. Runner compatibility remains pending, without another test cycle.

Private evidence: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/saturno-thinpool-20261121/`. Sanitized incident evidence and coverage explicitly block the next Vault/ntfy batch without marking either migrated. Storage is not stable enough for new loads; neither a new production cutover nor complete recovery is claimed.
