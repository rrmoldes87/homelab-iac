#!/usr/bin/env python3
"""Converge only the dedicated ITTools guard using native nft atomically.

Native expressions avoid persisted xt_conntrack rules that iptables-nft cannot
read after a reboot. Never flush shared chains or modify other listeners.
"""
import ipaddress
import json
import subprocess

CHAIN = 'HM_ITTOOLS'
CLIENTS = [f'192.168.1.{n}/32' for n in range(202, 208)] + [f'10.244.{n}.0/24' for n in [0, 1, 2, 4, 5, 6]]

def read_chain(name):
    return json.loads(subprocess.check_output(['nft', '-j', 'list', 'chain', 'ip', 'filter', name], text=True))

def rules(data):
    return [x['rule'] for x in data['nftables'] if 'rule' in x]

def validate_owned(data, parent):
    current = rules(data)
    if not 2 <= len(current) <= len(CLIENTS) + 2:
        raise RuntimeError('Unexpected dedicated chain size')
    verdicts = [[k for e in r['expr'] for k in e if k in ('accept', 'drop', 'return', 'jump', 'goto')] for r in current]
    if verdicts[-2:] != [['drop'], ['return']] or any(v != ['accept'] for v in verdicts[:-2]):
        raise RuntimeError('Unexpected dedicated chain verdicts')
    for r in current[:-2]:
        matches = [e['match'] for e in r['expr'] if 'match' in e]
        sources = [v['right'] for v in matches if v.get('left') == {'payload': {'protocol': 'ip', 'field': 'saddr'}}]
        if len(sources) != 1:
            raise RuntimeError('Unknown source expression')
        source = sources[0]
        if isinstance(source, dict) and 'prefix' in source:
            source = str(source['prefix']['addr']) + '/' + str(source['prefix']['len'])
        if str(ipaddress.ip_network(str(source))) not in CLIENTS:
            raise RuntimeError('Unexpected allowed client')
    if sum(e.get('jump', {}).get('target') == CHAIN for r in rules(parent) for e in r['expr']) != 1:
        raise RuntimeError('Dedicated jump missing or duplicated')

def main():
    validate_owned(read_chain(CHAIN), read_chain('DOCKER-USER'))
    match = 'meta l4proto tcp ct direction original ct original ip daddr 192.168.1.92 ct original proto-dst 18081'
    lines = [f'flush chain ip filter {CHAIN}']
    lines += [f'add rule ip filter {CHAIN} ip saddr {ip} {match} counter accept' for ip in CLIENTS]
    lines += [f'add rule ip filter {CHAIN} {match} counter drop', f'add rule ip filter {CHAIN} counter return']
    spec = '\n'.join(lines) + '\n'
    subprocess.run(['nft', '-c', '-f', '-'], input=spec, text=True, check=True)
    subprocess.run(['nft', '-f', '-'], input=spec, text=True, check=True)
    after = read_chain(CHAIN)
    validate_owned(after, read_chain('DOCKER-USER'))
    assert len(rules(after)) == len(CLIENTS) + 2
    print('ITTools dedicated guard: 12 known clients; terminal DROP and RETURN verified')

if __name__ == '__main__':
    main()
