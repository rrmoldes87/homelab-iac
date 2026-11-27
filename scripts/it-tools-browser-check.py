#!/usr/bin/env python3
"""Real Chromium functional check through an existing private SSH tunnel; no deployment."""
import argparse
import base64
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:18881')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chromium', chromium_sandbox=True)
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url + '/base64-string-converter', wait_until='networkidle')
        boxes = page.locator('textarea')
        expect(boxes).to_have_count(4)
        value = 'IT-Tools migration: café ✓'
        encoded = base64.b64encode(value.encode()).decode()
        boxes.nth(0).fill(value)
        expect(boxes.nth(1)).to_have_value(encoded)
        boxes.nth(2).fill(encoded)
        expect(boxes.nth(3)).to_have_value(value)
        page.reload(wait_until='networkidle')
        expect(page.locator('textarea')).to_have_count(4)
        page.locator('textarea').nth(0).fill('restart-check')
        expect(page.locator('textarea').nth(1)).to_have_value(base64.b64encode(b'restart-check').decode())
        page.screenshot(path=str(output.with_suffix('.png')), full_page=False)
        browser.close()
    result = {'passed': not errors, 'browser': 'real Chromium, sandbox enabled',
              'functional_checks': ['Unicode base64 encode', 'Unicode base64 decode', 'deep-link reload and encode'],
              'page_errors': errors, 'target_url': args.url,
              'tls_verification': 'normal Chromium CA validation' if args.url.startswith('https://') else 'not applicable',
              'sso_tested': False}
    output.write_text(json.dumps(result, indent=2))
    output.chmod(0o600)
    os.chmod(output.with_suffix('.png'), 0o600)
    print(json.dumps(result))
    return 0 if result['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
