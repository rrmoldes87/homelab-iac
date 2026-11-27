# DefectDojo — cierre de producción Talos → VM103

Estado: producción en VM103, escritor único. Cierre de 2026-11-20; alcance limitado a DefectDojo. No se ha iniciado otro workload.

## Destino y durabilidad

- URL: `https://dojo.<TU_DOMINIO>`; autenticación web conservada mediante Authentik.
- Compose `homelab-defectdojo`; configuración `/etc/homelab-defectdojo/compose.json`, datos `/var/lib/homelab-defectdojo`.
- Cinco servicios con imágenes exactas fijadas por digest: PostgreSQL, Redis, uwsgi, nginx y worker. Se preservaron secretos existentes y media; no se publican aquí.
- `homelab-defectdojo.service` habilitado y activo. Compose usa `restart: unless-stopped`; systemd inicia mediante `up -d --no-recreate` y detiene mediante `stop`, conservando contenedores y red.
- Configuración instalada idéntica por SHA-256 a los archivos del repositorio. Cierre sin recreaciones ni reinicios: IDs, StartedAt y RestartCount de **todos** los contenedores iguales antes/después. No se ha ensayado reboot del host.

## Origen, GitOps y endpoints internos

Commit de cutover en `<TU_USUARIO_GIT>/homelab` (checkout `homelab-ittools-bridge`): `3954d503a3606c46b82d2dcb660ea6c0301caf70`; ArgoCD `app-defectdojo` Synced/Healthy sobre esa revisión.

Los cuatro deployments `dojo-web`, `dojo-celery-worker`, `dojo-db` y `dojo-redis` tienen réplicas deseadas y reales a cero. No quedan pods en el namespace. Los dos PVC originales permanecen Bound; **no constituyen una copia actualizada del escritor destino** después del cutover.

Se conservaron DNS/puertos de los Services mediante EndpointSlices listos hacia VM103:

| Service DNS bajo `defectdojo.svc.cluster.local` | Puerto de Service | VM103 |
|---|---:|---:|
| `dojo-web` | 8080 | 192.168.1.92:18108 |
| `dojo-db` | 5432 | 192.168.1.92:18109 |
| `dojo-redis` | 6379 | 192.168.1.92:18110 |

Prueba desde un pod temporal no privilegiado, imagen exacta ya usada por la aplicación: login interno **200**, API anónima **403**, Redis **PONG**, PostgreSQL negociación SSL **N** (respuesta de protocolo válida, no afirmación de TLS). Pod eliminado. El script inicialmente usaba el puerto 80 en vez del puerto de Service 8080; se corrigió **el checker**, sin modificar endpoints. Slices antiguos vacíos no aportan destinos. Los puertos directos 18108–18110 están bloqueados desde la máquina de gestión.

## Aceptación y recuperación realmente probadas

- HTTPS con validación TLS correcta; `/login` **302 hacia Authentik**.
- API autenticada de sólo lectura: productos, findings y usuarios **200**; petición anónima rechazada **401** en HTTPS. Credencial temporal del probe retirada; tabla de tokens nuevamente vacía.
- Cinco contenedores en ejecución, cero reinicios y sin OOM; worker activo. Control Celery `pong` comprobado previamente. En este cierre no se enviaron tareas, notificaciones ni jobs sintéticos.
- Restore inicial consistente: dump PostgreSQL igual al origen, hashes media iguales, `pg_amcheck` correcto, RDB con checksum válido y cola Celery vacía en la copia inicial.
- Con web parado se aplicaron migraciones Django pendientes necesarias para las imágenes exactas existentes. Comprobación final de migraciones sin pendientes y amcheck de la base de aplicación satisfactorios. Las bases auxiliares `postgres`/`template1` no tienen amcheck instalado y fueron omitidas por la herramienta.
- Backup PostgreSQL **posterior** al ajuste de esquema restaurado en contenedor separado, imagen exacta, `network none`, con igualdad de esquema normalizado, recuentos principales y amcheck. Checker detenido y conservado.
- **No probado:** login SSO completo en navegador, rollback completo de la aplicación ni reboot. Restauración PostgreSQL aislada **no equivale** a rollback integral ni valida restauración conjunta de media/Redis posteriores al cutover.

No se debe reactivar el origen con los PVC antiguos: para un rollback real hay que detener primero los escritores destino, respaldar/restaurar el estado actual de PostgreSQL, media y Redis, validar compatibilidad del esquema, y sólo entonces invertir rutas/escritor. No se ejecutó ese procedimiento ni se promete conmutación inmediata.

Avisos heredados observados: clave de cifrado de credenciales por defecto y `ALLOWED_HOSTS=*`. No se cambian en este cierre: rotar la clave sin tratamiento de credenciales almacenadas puede invalidarlas. No se amplía el alcance a hardening.

## Capacidad y evidencias

Ampliación previa ya completada: disco 48 → 96 GiB tras backup PBS y restore aislado VM104. Filesystem raíz pasó de 49.754.808.896 a 99.702.718.464 bytes; libres inmediatamente tras crecimiento 58.920.259.584 bytes (41% usado). Al cierre DefectDojo: libres 57.193.615.360 bytes, 43% usado; memoria disponible 2.805 MiB. No se repitió la ampliación.

Evidencias privadas bajo `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/defectdojo-production/`:

- `closure-manifest.json`: rutas absolutas, SHA-256, commits y verificación remota.
- `closure-health.json`, `https-closure.json`, `service-dns-network.json`, `capacity-closure.txt`.
- `restore.json`, `postcutover-restore-proof.json`, `current-pg.dump`, `schema-alignment.private.log`.
- `service-durability.txt`, `durability-no-restarts.json`, `cutover.json`.

Gate de ampliación: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/vm103-expand-96g/`.
Cobertura local: `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json`; los cuatro deployments constan con cutover/backup/restore/aceptación acotada verificados y rollback/SSO navegador/reboot **no verificados**. Los campos `images` originales son inventario de origen; las imágenes exactas destino están en Compose y evidencias. No se publican backups, secretos ni evidencias privadas en Git.
