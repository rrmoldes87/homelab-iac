# Actual Budget — migración productiva aceptada

Fecha: 2026-11-20. URL: https://actual.<TU_DOMINIO>. Configuración: `compose/actual-budget/compose.json`; unidad: `systemd/homelab-actual-budget.service`.

Cierre, capacidad real y candidatos siguientes: [informe ES/EN del lote](BATCH-CLOSURE-2026-11-20.es-en.md). El siguiente lote queda en gate de capacidad; no se amplió almacenamiento ni se migró otra carga.

## Estado y alcance

- Imagen fuente exacta, versión 26.11.0: `docker.io/actualbudget/actual-server@sha256:06cf186569cf58d93e12659ff1a517b65b5b0ebee7050a3991d4bd8a1d398da6`. No se actualizó la aplicación.
- Único escritor: Docker VM103 `192.168.1.92:18107`, unidad `homelab-actual-budget.service` habilitada. Puerto limitado por el cortafuegos de listeners del clúster.
- Estado activo: `/var/lib/homelab-actual-budget-v2/data`; configuración instalada: `/etc/homelab-actual-budget`.
- Se mantiene el Service `actual-budget:5006`, selector retirado y EndpointSlice `actual-budget-vm103` a VM103:18107. Ingress, DNS y TLS no cambian.
- Deployment Talos fijado al mismo digest, réplicas 0; PVC `actual-budget-data` conservado Bound, UID `6ebfaac6-5011-4e8e-8cdf-a8ddcc4adbea`. El PVC es una copia detenida, no el estado actual tras el corte.
- Unidad específica solamente: no se reinstaló Docker, no se reinició el host ni servicios ajenos. 42 contenedores ajenos conservaron ID, StartedAt y contador de reinicios.

## Integridad y aceptación real

Se detuvo el escritor mediante GitOps y se esperó la desaparición de sus pods antes de copiar el directorio completo con SQLite, WAL y blobs. Hash de cada archivo fuente y destino idéntico antes del arranque; integridad SQLite y recuentos de todas las tablas coincidentes después del arranque.

HTTPS con CA normal: página 200, inventario autenticado idéntico (un presupuesto), descarga autenticada del blob con SHA-256 idéntico al original y acceso anónimo rechazado 401. Se comprobó el Service DNS desde el clúster. Estas pruebas se repitieron tras reiniciar exclusivamente la unidad destino. Argo `app-actual-budget`: Synced/Healthy en `fe6030f5d13523892e8fd89e88bf76153d00dbaa`.

No se abrieron pantallas con navegador, no se modificaron presupuestos, no se lanzaron sincronizaciones bancarias ni se probó un reinicio del host. No se afirma aceptación de esas operaciones.

## Incidencia y rollback comprobado

El primer arranque se revirtió porque la sonda esperaba `status=ok`, pero `/info` devuelve `build.version`. La aplicación no había fallado. Se detuvo el destino, archivó su estado actual completo, devolvió al PVC con ambos escritores detenidos y verificó la igualdad de todos los hashes. Se restauró la ruta/escritor fuente; tras convergencia se comprobó HTTPS y el inventario autenticado. El segundo intento partió de otra copia fría actual y usa el directorio `-v2`. El antiguo `/var/lib/homelab-actual-budget/data` queda detenido como evidencia, nunca debe arrancarse sobre datos antiguos. La reversión ejercitada fue posterior al arranque del destino y anterior al cambio de ruta; no fue una prueba de reversión tras nuevas escrituras financieras.

## Recuperación con datos actuales — orden obligatorio

1. Coordinar una ventana sin clientes. Mantener el Deployment fuente en 0 y el Service apuntando al destino hasta preparar la reversión.
2. Detener **solo** `sudo systemctl stop homelab-actual-budget.service` en VM103. Confirmar que no queda el contenedor escritor. No usar `down -v`, no arrancar el PVC antiguo.
3. Con el destino detenido, `sudo tar cpf - -C /var/lib/homelab-actual-budget-v2/data .` hacia un archivo privado fuera de Git. Conservarlo antes de cualquier reemplazo.
4. Crear un pod auxiliar sin aplicación en el nodo del volumen con el digest fijado y el PVC montado en escritura. Confirmar otra vez ausencia de ambos escritores. Respaldar el contenido antiguo del PVC antes de reemplazarlo; extraer el archivo **actual** completo, preservando UID/modos. Archivar de vuelta desde el PVC y comparar hashes archivo a archivo. Comprobar `PRAGMA integrity_check` con todas las SQLite sin escritores.
5. En `homelab.git`, `k8s/apps/actual-budget/actual-budget.yaml`: restaurar `spec.selector.app.kubernetes.io/name: actual-budget` en el Service, retirar el EndpointSlice manual `actual-budget-vm103` y poner réplicas 1 conservando el digest exacto. Commit/push solo al repositorio autorizado; leer SHA remoto y esperar Argo Synced/Healthy, rollout y endpoints fuente.
6. Verificar HTTPS, sesión existente, inventario y descarga del blob; retirar el pod auxiliar. Mantener VM103 detenida. Nunca activar ambos escritores. Para volver a VM103 repetir copia fría **desde el estado fuente actual**, no reutilizar una copia anterior.

El script privado usado en el lote implementó la devolución del estado actual y comprobó hashes durante la incidencia; no ejecutar a ciegas sus fases de migración ya completadas. Una futura reversión requiere un nuevo archivo actual, no los tar de aceptación.

## Evidencias privadas y referencias

- `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/actual-budget-production-attempt2/result.json`
- Mismo directorio: `cold-copy-verification.private.json`, `sqlite-before.private.json`, `sqlite-after.private.json`, `download-and-restart-acceptance.json`, `unrelated-lifecycle.json`, archivos fríos privados.
- Primer intento: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/actual-budget-production/rollback-current-verified.json` y archivos privados de devolución.
- Configuración activa: `665b3b06d8f3085bdf1a0cf1ebf2239d280f1c5f`; parada fuente: `fc4678481c1ba8495399e23fde23143f49e10696`; ruta: `fe6030f5d13523892e8fd89e88bf76153d00dbaa`.

La evidencia contiene datos personales y sesiones: no subir a Git ni publicar contenido. Los snapshots locales no equivalen a un backup externo automatizado. VM103 observado al cierre: 9941 MiB RAM total, 3601 MiB disponibles; disco 8.4 GiB disponibles, 82 % usado. No migrar indiscriminadamente las cargas grandes con ese margen. Nextcloud, DefectDojo y ntfy no forman parte de este corte; Nexus, monitores y autoreparación quedan fuera.
