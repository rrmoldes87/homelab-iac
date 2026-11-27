# IT-Tools: migración productiva aceptada

Autorización de publicación y cambios productivos recibida; repositorio privado nuevo. DNS, TLS, compresión y security headers permanecen en Kubernetes. El backend productivo es `it-tools-vm-transition:80` → `192.168.1.92:18081`. Deployment y Service originales se conservan.

## Aceptación real

- Commit inicial `b25ebd92f7ff73b2c1d39e9ee50d3ae6298eb526`; puente original `9b9bd5159766340c0c3219bf980ea2d372bc33ea`. ApplicationSet mantiene padres selfHeal/prune y delega únicamente IT-Tools al repo nuevo.
- Corte final `a1f76c9b7dc97a39eae37b39bb56615c76989c63`: Argo Synced/Healthy, Service/EndpointSlice al destino, HTTPS 200 con CA normal.
- Chromium real con sandbox: Base64 Unicode en ambos sentidos y recarga profunda; sin errores JS.
- Rollback productivo `fbd3aa8`: backend Kubernetes original, HTTPS y navegador correctos. Reaplicación del destino y nueva aceptación completa.
- Los 29 contenedores del snapshot del corte conservaron IDs, StartedAt y RestartCount. Origen 1/1 disponible.
- Las pruebas anteriores acreditan 282 assets por ambos Traefik, host incorrecto rechazado, listener systemd habilitado y stop/start. No equivalen a un reinicio completo de VM.

No hay middleware de autenticación en este ingress: no se afirma SSO. No hay watchdog automático. No se declara retirada de Kubernetes ni migración del TLS/DNS.

## Compose reproducible, sin ejecutar sobre producción

`compose/it-tools/compose.json` reproduce imagen, límites, bind, puerto y política reales del listener. Solo parametriza la ruta de assets privados, no contiene assets ni credenciales. La imagen ya debe existir y su digest debe coincidir.

En VM103, validar únicamente:

```sh
IT_TOOLS_HTML=/ruta/absoluta/html docker compose -p homelab-ittools-listener -f compose/it-tools/compose.json config --quiet
```

El listener existente está gobernado por `homelab-ittools-listener.service` y su configuración instalada en `/etc/homelab-ittools-listener/`. No ejecutar `up`, `down` ni reemplazar esa instalación durante una validación documental. `restart: no` es intencionado: systemd gobierna el arranque existente. La prueba de config no reinicia ningún contenedor.

## Rollback verificado y repetible

Cambiar solo el backend del ingress a `it-tools:80`, publicar, solicitar refresh Argo y esperar Synced/Healthy; comprobar HTTPS y ejecutar `scripts/it-tools-browser-check.py --url https://tools.<TU_DOMINIO> --output <ruta-privada>`. Mantener Service/EndpointSlice de transición disponibles para reaplicar. No pausar los padres ni parar el listener mientras el tráfico apunta a él. La reversión productiva ya fue ejecutada y validada.

Evidencias privadas fuera de Git: `~/ObsidianVault/work/homelab-migration/it-tools-production/` (estados, JSON Chromium, capturas, lifecycle). La referencia canónica del commit de aplicación final está en `final-application.json`; `repository.json` histórico contiene la publicación inicial.
