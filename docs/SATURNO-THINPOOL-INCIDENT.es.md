# Saturno: agotamiento thin pool — mitigación parcial, incidente abierto

No es una migración aceptada. Se bloquea el siguiente lote Vault/ntfy por riesgo de almacenamiento acreditado.

## Medición y acción ejecutada

- `pve/data` estaba al 100%; los metadatos no estaban agotados.
- Antes de actuar se midieron LV/VG, estado device-mapper, salud, configuración de autoextend y logs de backup/kernel. Se guardó `vgcfgbackup` en `/root/homelab-migration/saturno-thinpool-20261121/pve-before.conf` (copia de metadatos, NO backup de datos).
- Se añadieron **8 GiB del VG existente**, sin ampliar Urano/VM103, quitar discos ni borrar backups. Pool final: 160230801408 bytes, datos **94,64%**, metadatos **4,40%**, reserva VG **8594128896 bytes**. Device-mapper está `rw`, sin `needs_check` mostrado; esto NO certifica los sistemas de archivos invitados.
- Autoextend efectivo: umbral 80%, incremento 20%. La reserva actual no puede cubrir ese incremento; no se alteró la configuración para eludir el bloqueo ni el cron de backup.

## Alcance exacto y daños pendientes

El job diario rechazó snapshots de CT **101,109,111,122,131,140,141,143,145** con `Cannot create new thin volume, free space in thin pool pve/data reached threshold.` VM117 y VM120 sí completaron sus backups.

Las pruebas de creación de un archivo propio de un byte más `fsync` confirman:
- CT111 `vaultwarden`: sólo lectura, aunque systemd informa activo. No confundirlo con el Deployment Kubernetes `vault`.
- CT140 `syncthing`: sólo lectura.
- CT141 `obsidian-web`: `ENOSPC`, raíz al 100%, 0 bytes disponibles.
- CT101,109,113,122,131,143,145: prueba de escritura/fsync correcta; no equivale a aceptación integral de sus aplicaciones. Los archivos de prueba se retiraron.

## Recuperación y límites

PBS-Truenas está activo y tiene espacio. Los backups más recientes inventariados de CT111/140/141 son del **18 de noviembre**; no se ha probado su restauración. El intento adicional recuperable de CT111/140, en unidad systemd durable `homelab-saturno-emergency-backup-20261121.service`, terminó fallido por el mismo umbral. Se usó `--remove 0 --prune-backups keep-all=1`; no se podó ni eliminó ningún backup.

No se forzaron remontajes rw, no se ejecutó fsck sobre discos montados y no se detuvieron servicios para ocultar los fallos. La recuperación exige copia independiente de datos actuales, reserva medida, restauración aislada y validación antes de reparación offline. No consumir a ciegas los 8 GiB restantes. El crecimiento del pool no arregla el tamaño del filesystem de CT141.

VM103: 87%, 13120339968 bytes disponibles; no recibió volúmenes nuevos. VM117 permanece apagada; run269 sigue `waiting`, sin lanzarlo. No se tocó Nexus, el resto de Kubernetes, TrueNAS, monitores ni la programación de backup. Compatibilidad del runner pendiente, sin otro ensayo.

Evidencia privada: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/saturno-thinpool-20261121/`. `saturno-thinpool-evidence/incident.json` y cobertura registran el bloqueo sin marcar Vault/ntfy migrados. El estado no es estable para continuar cargas; no hay servicio nuevo aceptado ni una reparación integral fingida.
