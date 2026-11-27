#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
install -m 755 "$ROOT/tools/hooks/pre-commit" "$ROOT/.git/hooks/pre-commit"
echo "Installed pre-commit hook -> $ROOT/.git/hooks/pre-commit"
