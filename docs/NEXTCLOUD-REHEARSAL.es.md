# Nextcloud aplicación + PostgreSQL — ensayo aislado, producción NO migrada

## Resultado y límites

Producción sigue disponible en Talos: `https://nextcloud.<TU_DOMINIO>`. Aplicación, PostgreSQL y Valkey conservan una réplica Ready cada uno; los pods y sus reinicios no cambiaron. Ambos PVC siguen Bound. HTTPS `/status.php` y `/login`: 200 con TLS validado. No se cambió mantenimiento, rutas, réplicas, ArgoCD, monitores ni autorepair. Nexus quedó excluido.

El ensayo recuperó PostgreSQL y Nextcloud en VM103 con imágenes exactas por digest, sin red externa, puertos publicados ni schedulers. Se verificaron:

- Backup PostgreSQL `pg_dump --format=custom --serializable-deferrable`, restore sin errores, igualdad exacta de datos/secuencias, `pg_amcheck` y persistencia tras reinicio del PostgreSQL aislado.
- Hashes de todos los ficheros copiados, excepto logs activos de Nextcloud, antes de cambiar configuración exclusivamente de la copia.
- Nextcloud 35.0.0 instalado, sin mantenimiento ni actualización DB pendiente; usuario original recuperado sin publicar identidad.
- HTTP local `/status.php` y `/login` 200; usuario sintético sólo en copia aislada, WebDAV crear/leer/borrar satisfactorio y usuario eliminado.
- Tres contenedores de ensayo apagados/conservados, `restart=no`, sin OOM. Fallo inicial por permisos PostgreSQL corregido con UID/GID 70:70; contenedor fallido apagado conservado.
- Los contenedores preexistentes de VM103 fuera de Nexus conservaron ID, StartedAt y RestartCount.

**La captura combinada NO es un backup atómico DB+ficheros.** Los hashes de ficheros y la huella de datos/secuencias DB permanecieron iguales durante la copia online; eso acredita quietud observada, no bloqueo global de escritores ni coherencia atómica entre volúmenes. El backup PostgreSQL sí es transaccional. No habilita corte ni rollback completo de aplicación. Logs activos se excluyeron del tar.

No se repitió el ensayo sintético de caché aceptado anteriormente. Valkey efímero sólo formó parte del entorno de aplicación; no se da por validada la integración completa de sesiones/locking/caché de producción. No se probaron SSO navegador, correo, jobs, integraciones externas ni reboot del host.

## Fuente y almacenamiento

Namespace `nextcloud`; deployments `nextcloud`, `nextcloud-db`, `nextcloud-redis`. PVC `nextcloud-html` (10Gi) montado en `/var/www/html`; PVC `nextcloud-db` (10Gi) en `/var/lib/postgresql`. Ambos CSI Longhorn, no NFS directo. Directorio de datos `/var/www/html/data`, aproximadamente 100MiB; árbol HTML completo aproximadamente 1,7GiB. La aplicación `files_external` está deshabilitada. No se descubrió volumen NFS de aplicación; VM103 no mostró montajes NFS activos.

No se publican configuración de usuarios, credenciales, dumps ni contenido de ficheros.

## Capacidad y aislamiento

Se consultaron VM103 y los tres hosts del inventario (Saturno, Jupiter, Urano), sin cambiar asignaciones. VM103 tenía 2.921.759.744 bytes de RAM disponibles y 57.193.615.360 bytes de disco libres. Admisión del ensayo: más de 2.300MiB disponibles y 12GiB libres.

Límites explícitos: aplicación 768MiB, PostgreSQL 256MiB, Valkey 64MiB; total 1.088MiB, sin swap adicional, CPU limitada. No se amplió RAM ni se desplegó en otro host. Esto prueba que el ensayo cabe, **no** dimensiona concurrencia/capacidad de producción.

Después del ensayo y con contenedores apagados: RAM disponible 2.918.592.512 bytes; disco libre 51.783.311.360 bytes, 49% usado. Copia recuperada y artefactos remotos retenidos ocupan 2.779.031.109 bytes en `/var/lib/homelab-nextcloud-rehearsal`; también se retienen imágenes exactas. No se borró la recuperación para aparentar más capacidad.

## Gates de producción y patch local

El repositorio `<TU_USUARIO_GIT>/homelab` es **PÚBLICO**. No se modificó su checkout, aplicó patch, hizo commit ni publicó allí. Existe sólo un patch privado revisable, validado con `git apply --check`:

`/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/nextcloud-app-db/nextcloud-cutover.UNAPPROVED.patch`

**NO APLICAR:** propone cero réplicas y EndpointSlices para puertos 18111–18113 en VM103; son propuestas no reservadas ni verificadas, y no hay destino de producción escuchando. Aplicarlo ahora interrumpiría el servicio. Requiere autorización específica de publicación GitOps pública, configuración/seguridad y presupuesto de producción, copia actual DB+ficheros atómicamente coherente mediante mantenimiento controlado o mecanismo equivalente soportado, destino listo, recuperación con datos actuales, aceptación y comprobación de endpoints internos/externos. No se ha iniciado ese corte.

## Evidencias privadas

Directorio `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/nextcloud-app-db/`: `closure-manifest.json`, `capture.json`, `restore-acceptance.json`, `images.json`, `source-status-final.json`, `https-final.json`, `destination-no-restarts.json`, `capacity-final.txt`, `public-patch-gate.json`. Dumps, tar, manifiestos de hashes y configuraciones privadas sólo allí y en la copia remota protegida. Cobertura: `/home/<TU_USUARIO>/.config/homelab-migration/coverage.json`; aplicación y DB con restore/aceptación aislada, cutover/rollback falsos; backup combinado de aplicación NO verificado.
