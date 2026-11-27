#!/usr/bin/env python3
"""Dedicated per-listener chains. Never flush shared Docker rules."""
import argparse,subprocess
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--protocol',choices=['tcp','udp'],default='tcp');a=p.parse_args();assert a.port==6881 or 18083<=a.port<=18115
assert a.protocol=='tcp' or a.port==6881
chain='HM_VM_'+str(a.port)+('_UDP' if a.protocol=='udp' else '')
allow=['192.168.1.202/32','192.168.1.203/32','192.168.1.204/32','192.168.1.205/32','192.168.1.206/32','192.168.1.207/32','10.244.0.0/24','10.244.1.0/24','10.244.2.0/24','10.244.4.0/24','10.244.5.0/24','10.244.6.0/24']
def run(*v,check=True):return subprocess.run(['iptables','-w','5',*v],check=check,capture_output=True)
match=['-p',a.protocol,'-m','conntrack','--ctorigdst','192.168.1.92','--ctorigdstport',str(a.port),'--ctdir','ORIGINAL']
rules=[[*match,'-s',ip,'-j','ACCEPT'] for ip in allow]+[[*match,'-j','DROP'],['-j','RETURN']]
if run('-S',chain,check=False).returncode:
 run('-N',chain)
 for r in rules:run('-A',chain,*r)
else:
 for r in rules:
  if run('-C',chain,*r,check=False).returncode:raise SystemExit('Existing dedicated chain differs; refusing modification')
if run('-C','DOCKER-USER','-j',chain,check=False).returncode:run('-I','DOCKER-USER','1','-j',chain)
print('Dedicated listener rules verified:',a.port)
