#!/usr/bin/env bash
set -euo pipefail
docker rm -f homelab-cadvisor 2>/dev/null || true
docker run -d --name homelab-cadvisor --restart unless-stopped \
  --network homelab-monitoring_default \
  --memory 160m --cpus 0.25 \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  gcr.io/cadvisor/cadvisor:v0.49.1 \
  --housekeeping_interval=30s \
  --docker_only=true \
  --disable_metrics=advtcp,cpu_topology,cpuset,hugetlb,memory_numa,process,referenced_memory,resctrl,sched,tcp,udp
