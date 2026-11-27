# NetAlertX — ensayo recuperable, corte bloqueado

Estado: **no migrado**, origen Kubernetes operativo y único escritor. No se alteraron Deployment, PVC, Service, Ingress, configuración ni credenciales originales. HTTPS y HTTP origen devuelven 200.

Se restauró en VM103 un snapshot transaccional SQLite generado mediante backup API (incluye WAL), con configuración copiada junto al snapshot. Integridad SQLite correcta en local y dentro de la imagen exacta, 17 tablas; SHA-256 del tar idéntico tras transferencia. No constituye snapshot frío de toda la aplicación ni aceptación funcional.

Imagen: `ghcr.io/netalertx/netalertx@sha256:ebce55cdbccc0f71544e6997541fe81db803b8c8bec3079435b8cd0a40d49b7e`.

Bloqueo real: SCAN_SUBNETS usa `cni0` y `flannel.1` del nodo Talos; VM103 sólo preserva la interfaz LAN `eth0`. Omitir los escaneos overlay, inventar interfaces o arrancar plugins SMTP/SYNC/WORKFLOWS contra una topología distinta modificaría el alcance del servicio. No se hizo. El contenedor de verificación ejecutó exclusivamente SQLite, sin red, raíz y datos read-only, sin iniciar escáneres ni notificaciones. Las capabilities NET_ADMIN/NET_RAW fueron necesarias por los file capabilities del Python de esta imagen, incluso sin red.

No hay destino productivo, aceptación autenticada, prueba de persistencia del servicio ni rollback de corte: no hubo corte. DB recuperable demostrada; backup integral de aplicación todavía pendiente. ntfy continúa bloqueado por exportación consistente de caché en memoria no demostrada; no se aceptó perder mensajes.

Capacidad (muestra final antes/después): RAM disponible 2547175424 / 2544099328 bytes; disco libre 40132554752 / 40132444160 bytes. El pull inicial se realizó antes de esta muestra final de reintento. No se habilitó servicio nuevo ni se cambió firewall. Nexus, autorepair y Kubernetes permanecen intactos. Headlamp se descartó como alternativa inmediata: usa identidad in-cluster y conserva dependencia del API Kubernetes; no se trasladaron privilegios automáticamente.

Evidencia privada: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/netalertx-preflight-20261120`. Copia en VM103: `/var/lib/homelab-netalertx-rehearsal/snapshot.private.tar`. No publicar backups, configuración, inventario de dispositivos ni evidencias privadas. Se requiere rediseño explícito de paridad overlay/notificaciones antes de corte; no repetir ensayos cerrados.
