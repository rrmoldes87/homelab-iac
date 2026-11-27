# TEI — migración productiva VM103

Incidencia de corte: las pruebas detectaron ruta a pods obsoletos al retirar el selector: coexistían Endpoints legado y EndpointSlices de controlador/mirroring. Se eliminaron sólo esos objetos obsoletos, manteniendo `tei-vm103`; después se repitieron pruebas reales por DNS/Service y reinicio. Hubo fallo transitorio observado, por lo que no se afirma disponibilidad ininterrumpida.

Estado: **aceptado**, imagen `ghcr.io/huggingface/text-embeddings-inference@sha256:8de25e75ce39617f17f2f6c77d60a4f75b65e779ed5005420eb1400072a15c1c`. Backend `192.168.1.92:18115`; nombre interno conservado `tei.mlops.svc.cluster.local:80`.

Selección: inferencia sin DB, sin credenciales de API en origen y modelo inmutable ~457 MiB; Vault/Forgejo/Authentik requieren reconciliar estado/secretos/dependencias, Immich/SonarQube mayor presupuesto. Restauración medida 1.37 GiB, ~1 GiB RAM disponible durante ensayo; límite 2 GiB y 2 CPU. No se añadió carga sin medir.

Backup de caché con hashes antes/después idénticos, archivo transferido por SHA256; restauración con imagen exacta sin red y embeddings 384 dimensiones. Configuración durable systemd habilitada, caché producción read-only y HF_HUB_OFFLINE=1, sin escritor duplicado de datos de aplicación. Réplicas Talos 0/sin pods; Argo Healthy/Synced en `eb17e09224f4076c4c1d1dc9ce6e3c91320ef5d7`. Convergencia explícita tras refresh duro: no atribuir fencing durable al primer apply mientras Argo conservaba revisión anterior.

Pruebas reales: embedding origen/restauración/destino, diferencia máxima 5.599999999827965e-08; DNS y Service desde pod real; health 200 y embeddings tras reinicio systemd. Acceso LAN no autorizado termina curl 28/HTTP000 (timeout, NO401). No hay autenticación nativa configurada ni endpoint público HTTPS de TEI; no se inventa prueba de login. Firewall limita origen a nodos/pods Talos. Sin prueba de reboot host ni rollback posterior al corte. Recuperación: conservar tar/modelo y manifiesto anterior en `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/tei-production`; restaurar GitOps anterior, esperar origen Ready antes de revertir ruta y deshabilitar destino; no borrar copia de modelo, el emptyDir original no es backup durable.

NetAlertX: redes 10.244.5.0 pertenecen al overlay CNI/Flannel Kubernetes, frente LAN 192.168.1.0/24. No se retiran escaneos todavía: diseño final pendiente al desmontar K8s; no nuevas redes/interfaces. Nexus/monitores/autorepair y apagado K8s intactos.

Evidencias, capacidad antes/después y límites: `/home/<TU_USUARIO>/ObsidianVault/work/homelab-migration/tei-production`. Configuración `bc5713640992598ffcc0154fd2224ddace31f338`; GitOps `eb17e09224f4076c4c1d1dc9ce6e3c91320ef5d7`. Sólo infraestructura mínima en GitOps público; caché/evidencias/configuración documental privadas.
