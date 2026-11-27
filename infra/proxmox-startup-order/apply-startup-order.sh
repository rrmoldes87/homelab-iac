#!/usr/bin/env bash
# Declarative Proxmox VE startup order (power-loss resilience, production guests only).
# Stopped/recovery guests (104, 105, 106, 149, 150, 7000-9001) keep onboot=0 untouched.
set -euo pipefail

ssh urano '
  pct set 132 --startup "order=1,up=15"
  qm  set 108 --startup "order=1,up=45,down=120"
  pct set 148 --startup "order=2,up=15"
  pct set 147 --startup "order=2,up=15"
  pct set 146 --startup "order=3,up=20"
  qm  set 103 --startup "order=3,up=20"
  pct set 142 --startup "order=4"
  pct set 144 --startup "order=4"
  pct set 100 --startup "order=4"
'
ssh saturno '
  pct set 131 --startup "order=1,up=15"
  pct set 109 --startup "order=1,up=15"
  pct set 111 --startup "order=2,up=15"
  pct set 122 --startup "order=2,up=15"
  pct set 113 --startup "order=3,up=20"
  pct set 145 --startup "order=3,up=15"
  pct set 151 --startup "order=3,up=15"
  pct set 153 --startup "order=3,up=15"
  pct set 140 --startup "order=4"
  pct set 141 --startup "order=4"
  pct set 143 --startup "order=4"
  pct set 101 --startup "order=4"
'
ssh jupiter '
  pct set 130 --startup "order=1,up=15"
  pct set 152 --startup "order=1,up=15"
  qm  set 107 --startup "order=2,up=20"
  pct set 124 --startup "order=3,up=10"
  pct set 110 --startup "order=3,up=10"
  pct set 123 --startup "order=3,up=10"
  pct set 154 --startup "order=3,up=10"
  pct set 102 --startup "order=4"
'
