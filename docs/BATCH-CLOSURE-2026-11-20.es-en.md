# Cierre del lote / Batch closure — 2026-11-20

## Español

Actual Budget está aceptado en producción; ver [operación y rollback ES](ACTUAL-BUDGET.es.md) y [EN](ACTUAL-BUDGET.en.md). La matriz privada `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json` marca **solo su Deployment** con copia, restauración, función y corte verificados. Mantiene `rollback_verified=false`: se probó devolver datos actuales antes del cambio de ruta, no una reversión completa posterior al corte. No se convierten ensayos de componentes de otras aplicaciones en migraciones completas.

Se revalidó en vivo la aceptación del retiro anterior: **19 Deployments** y sus ReplicaSets/pods siguen ausentes; todos los PVC, Services, Ingress y EndpointSlices protegidos mantienen UID/contenido; sus aplicaciones Argo están Synced/Healthy y los **17** resultados HTTPS coinciden con el baseline. No se exige la revisión antigua a aplicaciones legítimamente reconciliadas después; la evidencia registra las revisiones observadas. Actual Budget devuelve HTTPS 200, conserva su PVC Bound/UID, tiene réplicas 0 en origen y Argo Synced/Healthy en `fe6030f5d13523892e8fd89e88bf76153d00dbaa`. Su unidad dedicada está activa/habilitada. No se escribieron datos financieros ni se invocaron bancos.

### Gate de capacidad: siguiente lote detenido, no siguiente migración

Inventario real: VM103 `compose-core`, **urano**, 2 vCPU, **10 GiB configurados** (9941 MiB visibles), disco `scsi0` **48 GiB**, raíz ext4. Raíz: **8.4 GiB libres, 82% utilizada**; memoria disponible observada 3599 MiB. No existe otra partición de datos con margen libre. Docker informa 25.49 GB de imágenes, solo 651 MB recuperables; build cache 0 B. El uso principal medido es containerd (25.86 GB), además de datos activos y copias de recuperación.

Para el siguiente lote se propone un **mínimo conservador de 10 GiB libres de raíz después de reservar imágenes, datos activos, copia consistente y restauración de prueba**, más el presupuesto de RAM de todos los componentes simultáneos. Es un gate de planificación de este lote, no una política previa ni un cálculo de uso de las aplicaciones todavía no medido. Con 8.4 GiB actuales ya no se cumple ni la reserva base; borrar 651 MB de imágenes no lo resuelve. No se ejecutó ninguna poda: imágenes sin contenedor también pueden ser necesarias para recuperación, y copias antiguas no son basura autorizada.

Proxmox confirma almacenamiento activo en urano: `local-lvm` **539.57 GiB disponibles**, `local` 74.09 GiB, `nvme-pool` 861.86 GiB. VM103 está en `local-lvm`. Medida concreta pendiente de decisión: **ampliar scsi0 de 48 a 96 GiB (+48 GiB)** en ese mismo backend; dejaría aproximadamente **491.57 GiB** físicos disponibles antes de otros cambios/crecimiento. No se ha reservado ni ejecutado. Requiere aprobar riesgo/operación y confirmar backup recuperable. Preflight de solo lectura ya comprobado: GPT con `/dev/sda1` como última partición física, EXT4 montado en `/`, `growpart` y `resize2fs` presentes. Propuesta, NO ejecutada: `qm resize 103 scsi0 +48G` en urano; comprobar tamaño nuevo en el invitado y luego `sudo growpart /dev/sda 1` y `sudo resize2fs /dev/sda1`; leer de vuelta tamaños y salud de servicios. La posible ampliación online evita asumir un reinicio permitido: si hiciera falta parar VM103, pedir ventana específica por impacto a servicios ajenos. No se amplía RAM ni se mueve almacenamiento en este lote.

El inventario Proxmox también devuelve PBS-Oracle inaccesible por timeout y avisos de configuración LVM duplicada; PBS-Truenas aparece activo. No se repararon backups ni se afirmó que exista un backup reciente/restaurable de VM103 a partir de ese estado. Confirmarlo es requisito previo a ampliar.

### Candidatos y condiciones pendientes

1. **DefectDojo:** ya hay ensayo de BD restaurada aceptado, no aceptación de aplicación. Medir imágenes/datos/media y RAM conjunta web + worker + PostgreSQL + Redis; reutilizar evidencia válida, pero hacer copia consistente actual, aceptar autenticación y función real antes del corte. No repetir el ensayo de BD sin cerrar un gap concreto.
2. **Nextcloud:** ensayo Redis solamente; pendiente presupuesto real de ficheros/BD/imágenes, snapshot coherente de BD y archivos, mantenimiento del escritor, integración de sesiones/locks y aceptación web con datos actuales.
3. **ntfy:** candidato pequeño por reevaluar solo cuando se resuelva `blocked-consistent-memory-export`; el ensayo de UI aislada no prueba conservación consistente de caché/estado en memoria ni autoriza publicaciones de notificaciones.

Nexus excluido. Talos sigue activo; sin cambios de monitores/autoreparación. Ningún candidato se declara migrado ni se arranca otro escritor por este informe.

### Evidencia privada

Directorio `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/actual-budget-production-attempt2/`:
- `result.json`: aceptación de la migración.
- `closure-health.json`: revalidación viva del cierre/limpieza y revisiones Argo.
- `proxmox-capacity.private.json`: capacidad consultada; no incluye credenciales.
- `coverage.before.private.json`: matriz previa al cierre.

La matriz completa y los datos financieros/credenciales permanecen fuera de Git. Este documento y los runbooks solo contienen resultados operativos y rutas locales, no contenidos privados.

## English

Actual Budget is accepted in production; see the linked operational runbooks. Only its Deployment entry in the private coverage matrix was updated: backup, restore, functional and cutover flags are true; `rollback_verified` remains **false**, because the initial current-data return happened before routing cutover, not a complete post-cutover rollback. Other component rehearsals were not promoted to full migrations.

Fresh closure checks passed: **19** retired Deployments and their dependent ReplicaSets/pods absent; all protected PVC/routing UIDs and contents unchanged; Argo applications Synced/Healthy; all **17** HTTPS results match baseline. Observed current Argo revisions are recorded rather than incorrectly requiring the old cleanup revision after later legitimate reconciliations. Actual Budget: HTTPS 200, source replicas 0, original PVC Bound with unchanged UID, Argo Synced/Healthy at the production bridge revision, dedicated destination unit active/enabled. No financial writes or bank calls.

**Capacity gate:** VM103 on **urano**, 2 vCPU, 10 GiB configured RAM, 48 GiB root disk on local-lvm. Guest: 8.4 GiB free/82% used, 3599 MiB available RAM. Docker images occupy 25.49 GB, only 651 MB reported reclaimable, build cache zero; recovery artifacts are not disposable. Proposed next-batch planning floor: **10 GiB root free after budgeting images, current data, consistent backup and test restore**, plus measured simultaneous component RAM. This is a conservative new planning gate, not a previously imposed policy or an unmeasured workload-size claim. Current capacity does not meet the base reserve; no pruning was performed.

Measured urano free storage: local-lvm **539.57 GiB**, local 74.09 GiB, nvme-pool 861.86 GiB. Concrete decision requested: expand the existing scsi0 from **48 to 96 GiB (+48 GiB)** on local-lvm, approximately **491.57 GiB** backend free afterward before other growth. Nothing reserved or changed. Read-only preflight confirms GPT with `/dev/sda1` physically last, root EXT4, and both `growpart` and `resize2fs` present. Pending approval and a verified recoverable backup, the proposed commands (NOT executed) are `qm resize 103 scsi0 +48G` on urano, verify the guest sees the new size, then `sudo growpart /dev/sda 1` and `sudo resize2fs /dev/sda1`; verify sizes and service health afterward. Do not assume reboot permission: request a specific window if online growth is unsuitable. No RAM or storage-placement change was made. PBS-Oracle timed out; PBS-Truenas is active, which does not prove a recent restorable VM103 backup. Duplicate LVM configuration warnings were observed, not repaired.

Next candidates: **DefectDojo** (database-only rehearsal, whole-stack capacity/media/authentication/function pending), **Nextcloud** (cache-only rehearsal, coherent DB/files snapshot, maintenance/locks/sessions and real acceptance pending), **ntfy** (small candidate but consistent in-memory export blocker unresolved; UI-only rehearsal is insufficient and notification publication is not authorized). Reuse valid evidence instead of repeating already accepted component tests. None is claimed migrated. Nexus excluded, Talos retained, monitoring/autorepair untouched.

Private evidence paths above contain the accepted migration result, fresh closure health, actual Proxmox capacity, and pre-update coverage backup. Full coverage, backups, authentication material and financial data stay outside Git.
