# Cortes productivos: Romifleur y Mealie

- Romifleur: VM103 `18086`, corte puente `131767be32db0511e86293c970c9a9c1ef3d1106`. Descarga sintética localhost de 2900 bytes, comparación exacta y API de carpetas; fixture eliminado. HTTPS y API públicos aceptados. Datos originales vacíos al congelar el proceso para copiar; Deployment original conservado a cero. Descargas posteriores son persistentes en `/var/lib/homelab-romifleur/data`.
- Mealie: VM103 `18087`, binario original fijado v3.30.0, quiesce `b926d2e903a97f65f673aa7ad1d6adbfceed81e4`, corte `7f38cc56f282ef5df97657e2b912dcf7ed3c177e`. Copia fría con todos los archivos SHA256 iguales; integridad SQLite y recuentos de todas las tablas iguales después de arrancar. HTTPS y `/api/app/about` iguales al origen, incluida configuración pública OIDC. No se ha probado login ni CRUD autenticado.
- Entorno Mealie: solo VM103, `/etc/homelab-mealie/env.private.json`, root 0600; no publicar ni copiar al repositorio. La unidad carga Compose público más este override privado.

## Reversión sin dos escritores

**No ejecutar un simple revert y arrancar el origen:** pueden existir datos nuevos en VM103. Los rollbacks siguientes están disponibles operativamente, pero NO se han ensayado en este lote.

1. Detener `homelab-<servicio>.service` en VM103; comprobar que no queda contenedor escritor. Mantener el Deployment Kubernetes a cero.
2. Archivar datos actuales en evidencia privada: Mealie `/var/lib/homelab-mealie`; Romifleur `/var/lib/homelab-romifleur/data`. Retener además las copias originales previas al corte.
3. Mealie: montar el PVC original mediante pod auxiliar sin proceso servidor, preservar su contenido anterior aparte y restaurar la copia actual íntegra, incluido SQLite/WAL. Romifleur: preparar PVC de retorno, restaurar las descargas actuales y montar ese PVC como `/app/data` en el Deployment original **antes de arrancarlo**. No confiar en su antiguo filesystem efímero.
4. Verificar SHA256 del retorno y, para Mealie, integridad SQLite. Solo entonces publicar el cambio GitOps que devuelve Ingress y una réplica al origen; no borrar la copia VM103.
5. Comprobar HTTPS, APIs y escritor único. Si no puede verificarse la transferencia, mantener el origen parado y recuperar el destino; no arrancar ambos.

Evidencias privadas: `work/homelab-migration/{romifleur-production,mealie-production}/`; no incluir backups, datos ni secretos en Git.
