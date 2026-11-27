# Mounted at /opt/homelab-ops/data/healthchecks/local_settings.py (CT 151)
# Allows internal LAN dead-man's switch pings directly to 192.168.1.97:8095 without Traefik dependency.
ALLOWED_HOSTS = ["hc.<TU_DOMINIO>", "192.168.1.97", "localhost", "127.0.0.1"]
