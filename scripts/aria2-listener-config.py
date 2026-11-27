#!/usr/bin/env python3
"""Make the authenticated engine reachable across Docker's published port.

Run only with the engine stopped. Firewall installation must precede this step.
Never changes or emits the existing RPC secret.
"""
import argparse
import pathlib


def configure(path):
    text = path.read_text()
    lines = text.splitlines()
    secrets = [s.split('=', 1)[1].strip() for s in lines if s.startswith('rpc-secret=')]
    if not secrets or not all(secrets):
        raise ValueError('Refusing network RPC without an existing nonempty secret')
    updated = '\n'.join(s for s in lines if not s.startswith('rpc-listen-all=')) + '\nrpc-listen-all=true\n'
    if updated != text:
        path.write_text(updated)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=pathlib.Path, required=True)
    configure(parser.parse_args().config)
