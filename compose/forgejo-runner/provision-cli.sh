#!/bin/sh
set -eu
# Offline: copy only from the already pinned local DinD container.
expected=6c71cfe71faff949a602946a4df4799b563232e79d0b8b6fd343d0ef081c9621
docker cp homelab-forgejo-runner-dind-1:/usr/local/bin/docker /var/lib/homelab-forgejo-runner/docker-cli
chmod 755 /var/lib/homelab-forgejo-runner/docker-cli
printf "%s  %s\n" "$expected" /var/lib/homelab-forgejo-runner/docker-cli | sha256sum -c -
