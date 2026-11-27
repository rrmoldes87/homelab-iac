# FlareSolverr productivo

Backend VM103 192.168.1.92:18082. DNS interno y Deployment original preservados. Compose, firewall y unidad systemd están en este repositorio; secretos y evidencias no.

Aceptación: sesión crear/listar, navegación real a example.com con HTTP200 y contenido, destrucción de sesión. Corte, rollback al original y corte final verificados. Commit final inicial `35464184fd0e4d2dd544501c18bb2d737e9a30d2`; rollback probado `b487352d4f1daf6153281c22387ccd800ab60722`. Los 29 contenedores previos mantuvieron ID, StartedAt y RestartCount.

## Reversión

Restaurar en Git el selector original del Service (`app.kubernetes.io/name: flaresolverr`) y poner `conditions.ready: false` en la EndpointSlice VM; publicar y comprobar Argo Synced/Healthy, ruta al pod original y navegación. La reversión probada conserva el Deployment y no borra datos.

En este clúster, quitar el selector dejó una EndpointSlice antigua y el objeto Endpoints antiguo volvió a crearla mediante mirroring. Para el destino se marcó **solo** Endpoints `flaresolverr` con `endpointslice.kubernetes.io/skip-mirror=true` y se retiró su slice autogenerada obsoleta. Para la reversión se retiró dicha etiqueta; el controlador regeneró la ruta original. No repetir un corte ignorando esta condición: comprobar que hay una única dirección lista, 192.168.1.92:18082.

No se afirma aceptación de desafíos anti-bot externos ni retirada del clúster/TLS/DNS.
