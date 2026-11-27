#!/bin/sh
curl -sf --max-time 2 http://127.0.0.1:8080/ping >/dev/null 2>&1
