# SearXNG productivo

VM103: listener 192.168.1.92:18083, Compose privado con Valkey; servicio systemd `homelab-searxng`. Configuración original copiada privadamente, cambiando únicamente el host Redis a `cache`; secretos fuera del repositorio. Origen sin PVC y keyspace Valkey vacío al preparar el corte; no se afirma migración de datos persistentes.

Producción `https://search.<TU_DOMINIO>`: TLS normal, HTTP200 y 54 resultados reales de brave/duckduckgo/google cse sin motores fallidos. La configuración y las credenciales originales permanecen privadas; se conserva el original en Kubernetes. Cambio del Ingress: `76d0eb560299800136cc6253b5419ad3f9936905` del repositorio original homelab.

Rollback disponible: revertir ese commit del Ingress, publicar en main y refrescar/verificar app-searxng; el Service original sigue apuntando a los pods originales. Comprobar HTTPS y una búsqueda con resultados. No se ejecutó el ciclo de rollback deliberado al ser un cambio de routing stateless; el comprobador revierte automáticamente si falla la aceptación. No se afirma SSO: el Ingress no lo configura.

Los manifiestos de `k8s/transitions/searxng` solo gestionan el Service y EndpointSlice del backend nuevo; la aplicación original conserva su ConfigMap, Deployments, Service e Ingress. Los padres GitOps siguen activos con selfHeal/prune.
