# Dependency-Track: frontend productivo

- Solo la interfaz se sirve desde VM103 `192.168.1.92:18084`; API y base de datos permanecen originales.
- Corte GitOps: `e633f283e3bfcbb2e46a20cd4639009f606676ab`. Ambas Applications Synced/Healthy.
- Origen conservado: Service `dependency-track/dtrack-frontend`. Destino: `dtrack-frontend-vm103`.
- Aceptación: TLS normal, HTML/config/JS/CSS iguales al origen conservado, API y discovery OIDC accesibles. Las vistas de login y «More options» son iguales en origen y producción; no se observó regresión OIDC. Login autenticado no probado.
- 32 contenedores previos conservan ID, StartedAt y RestartCount. Evidencia detallada solo en almacenamiento privado.
- Rollback disponible, no ejercitado en este corte: revertir el commit del Ingress anterior, publicar y verificar reconciliación y HTTPS. No eliminar originales.
- Comparación posterior al corte: abrir port-forward local al Service original y ejecutar `python3 scripts/dtrack-frontend-check.py --source http://127.0.0.1:18085 --destination https://dtrack.<TU_DOMINIO>`.
