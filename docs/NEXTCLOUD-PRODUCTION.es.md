# Nextcloud — producción aceptada en VM103

Fecha: 2026-11-20. URL: https://nextcloud.<TU_DOMINIO>.

## Resultado y escritor único

Aplicación Nextcloud 35, PostgreSQL 18 y Valkey están activos y saludables en VM103. Aplicación: `192.168.1.92:18111`; PostgreSQL: `:18112`; caché: `:18113`. Los tres Deployments originales de `nextcloud` están a cero; sus dos PVC siguen Bound y conservados. Los tres nombres Service DNS internos siguen funcionando mediante endpoints a VM103. No se apagó Kubernetes/Talos.

GitOps público de rutas: `c54f72dcf71894afb5201e938becd3dad66f3a55`. Configuración privada de concurrencia: `6bf864cc7e31622d9b00c8ada15e1d0d81429989`. Las publicaciones se comprobaron contra la referencia remota exacta. Imágenes fijadas por digest en `compose/nextcloud/compose.json`; no se actualizaron imágenes.

## Captura, recuperación y aceptación real

- Fuente en mantenimiento; aplicación/caché detenidas, dump PostgreSQL transaccional y posterior parada de DB; captura de archivos y DB con los escritores cercados. Es una captura conjunta consistente fuera de línea, **no un snapshot simultáneo atómico** de ambos volúmenes.
- Restauración de los archivos y DB; igualdad de manifiestos de archivos y datos/secuencias comprobada antes de abrir el escritor destino; `pg_amcheck` volvió a pasar en producción. Se conserva el dump y las imágenes físicas privadas.
- HTTPS con validación de certificado. DAV anónimo 401; usuario sintético independiente: PUT 201, GET 200 y contenido exacto, DELETE 204. Ninguna escritura de prueba en una cuenta real.
- Parada y arranque completo de aplicación/DB/caché: el archivo sintético permaneció y pudo leerse antes de eliminarlo. La cuenta sintética se eliminó y la lista original de usuarios quedó igual.
- Formulario nativo con CSRF y cabecera Origin llegó a `/apps/dashboard/` con 200. La prueba inicial omitía Origin y activaba la protección CSRF/SameSite: no era evidencia de contraseña incorrecta. No se atribuye este resultado a un navegador SSO completo.
- Configuración de locking Redis y ping desde Nextcloud verificados; caché efímera reconstruida tras reinicio. Los tres nombres DNS internos comprobados.
- Tres contenedores saludables, sin OOM; systemd habilitado y activo. Identidad, arranque y reinicios de **59 contenedores ajenos** iguales a la línea base.

## Incidente 137 y límites

El kernel de Urano registra OOM de `python3` en `/lxc/142/ns/system.slice/hermes-gateway.service`, RSS anónimo 3694796 kB. El helper de recuperación acumulaba un tar completo en memoria. **No fue OOM de la aplicación ni de VM103**. Se cambió esa transferencia a entrada/salida de archivos mediante subprocess, sin buffers completos. Se probó transferencia del archivo completo hacia SHA256 remoto y descarga tar acotada, sin escribir datos de usuarios. Esto no equivale a ejecutar un rollback productivo completo.

Límites: aplicación 1024 MiB/1.25 CPU, DB 384 MiB/0.5 CPU, Valkey 96 MiB/0.25 CPU; swap de cada contenedor limitado al mismo máximo. Apache: dos workers; PHP: 512M. Caché: 64 MiB, noeviction, sin persistencia RDB. No se amplió RAM ni se redistribuyeron recursos de otros servicios.

Capacidad medida antes/después: MemAvailable 3041435648 → 2947358720 bytes; disco libre 51796656128 → 46410481664 bytes. La reducción de disco incluye copias/intentos conservados. Uso observado aplicación/DB/caché: 106.1/36.57/3.883 MiB; es una muestra, no una garantía de pico. Margen exigido: RAM disponible >1200 MiB y disco >12 GiB.

## Evidencias y límites pendientes

Directorio privado: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/nextcloud-production/`. Referencia: `closure-manifest.json`, con hashes de evidencias y cobertura; pruebas `production-functional-acceptance.json`, `closure-health.json`, `exit137-diagnosis.json`, `streaming-recovery-helper-validation.json`. Cobertura local: `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json`.

No se declara verificado: reboot completo de VM103, navegador SSO, rollback productivo con datos actuales, backup periódico externo nuevo. No restaurar una copia antigua sobre el escritor activo: cualquier retorno exige mantenimiento, cercado de VM103 y transferencia consistente **de sus datos actuales** hacia los PVC conservados. Se conservan copias e intentos; no borrar por espacio sin otra recuperación verificada.

## Cierre global autorizado, todavía pendiente

Después de todas las migraciones/dependencias: balancear servicios por CPU/RAM/disco/carga medidos, verificar disponibilidad, persistencia y backups, y sólo entonces apagar ordenadamente las VMs Kubernetes/Talos. Apagar libera CPU/RAM, **no disco**; no autoriza eliminar VMs, discos, PVC ni copias. Nexus sigue excluido y es una dependencia que debe resolverse sin romperlo antes del apagado. Este pendiente es documental, no cron ni Kanban. No se inicia otro workload durante el cierre de Nextcloud.
