# Authentik Native OIDC Providers (CT 147)

Providers OIDC nativos creados en Authentik (`CT 147`, sin secretos en Git):

| Slug | App | Estado en cliente | Discovery URL |
| :--- | :--- | :--- | :--- |
| `grafana-oidc` | Grafana (`VM 103`) | **Activo y verificado** (`/etc/homelab-monitoring/grafana-oidc.env` `0600`) | `https://auth.<TU_DOMINIO>/application/o/grafana-oidc/.well-known/openid-configuration` |
| `open-webui` | Open WebUI (`CT 144`) | **Activo y verificado** (`/etc/open-webui/oidc.env` `0600`, secret rotado) | `https://auth.<TU_DOMINIO>/application/o/open-webui/.well-known/openid-configuration` |
| `immich` | Immich (`CT 146`) | Provider listo (`HTTP 200`); credenciales en `CT 147:/etc/homelab-oidc/providers.env` (`0600`) | `https://auth.<TU_DOMINIO>/application/o/immich/.well-known/openid-configuration` |
| `forgejo` | Forgejo (`VM 103`) | Provider listo (`HTTP 200`); credenciales en `CT 147:/etc/homelab-oidc/providers.env` (`0600`) | `https://auth.<TU_DOMINIO>/application/o/forgejo/.well-known/openid-configuration` |
| `paperless` | Paperless-ngx (`CT 145`) | Provider listo (`HTTP 200`); credenciales en `CT 147:/etc/homelab-oidc/providers.env` (`0600`) | `https://auth.<TU_DOMINIO>/application/o/paperless/.well-known/openid-configuration` |
| `audiobookshelf` | Audiobookshelf (`VM 103`) | Provider listo (`HTTP 200`); credenciales en `CT 147:/etc/homelab-oidc/providers.env` (`0600`) | `https://auth.<TU_DOMINIO>/application/o/audiobookshelf/.well-known/openid-configuration` |
