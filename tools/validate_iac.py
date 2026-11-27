#!/usr/bin/env python3
"""CI150 IaC Guardian: validates JSON, YAML, Python AST and blocks leaked secrets."""
import ast, json, pathlib, re, sys

try:
    import yaml
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCAN_DIRS = [
    ROOT / "infra",
    ROOT / "compose" / "homelab-ops",
    ROOT / "compose" / "jellyfin-saturno",
    ROOT / "compose" / "homelab-apps",
]
SECRET_PATTERNS = [
    (re.compile(r"\d{8,11}:AA[A-Za-z0-9_-]{30,}"), "Telegram Bot Token"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Private Key"),
    (re.compile(r'(CF_DNS_API_TOKEN|OPNSENSE_API_SECRET)\s*[:=]\s*[\'"`]?[A-Za-z0-9_-]{20,}'), "Hardcoded API Token"),
    (re.compile(r"auth_pass\s+(?!\$\{)[A-Za-z0-9_!@#%^&*-]{4,}"), "Hardcoded Keepalived VRRP Password"),
]

errors = []
checked = 0

for base in SCAN_DIRS:
    if not base.exists():
        continue
    for path in sorted(base.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        checked += 1
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for rx, label in SECRET_PATTERNS:
            if rx.search(text):
                errors.append(f"SECRET [{label}] in {rel}")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except Exception as e:
                errors.append(f"JSON syntax error in {rel}: {e}")
        elif path.suffix in (".yml", ".yaml") and yaml is not None:
            try:
                yaml.safe_load(text)
            except Exception as e:
                errors.append(f"YAML syntax error in {rel}: {e}")
        elif path.suffix == ".py":
            try:
                ast.parse(text, filename=str(rel))
            except SyntaxError as e:
                errors.append(f"Python AST error in {rel}: {e}")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)
print(f"IAC_GUARD_PASS: {checked} files validated (JSON/YAML/Python AST + secret scan)")
