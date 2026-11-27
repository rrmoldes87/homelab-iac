#!/usr/bin/env python3
"""Install only dedicated FlareSolverr DOCKER-USER rules; never flush shared chains."""
import subprocess
CHAIN='HM_FLARESOLVERR'
BIND='192.168.1.92';PORT='18082'
ALLOW=['192.168.1.202/32','192.168.1.203/32','192.168.1.204/32','192.168.1.205/32','192.168.1.206/32','192.168.1.207/32','10.244.0.0/24','10.244.1.0/24','10.244.2.0/24','10.244.4.0/24','10.244.5.0/24','10.244.6.0/24']
def run(*args,check=True):return subprocess.run(['iptables','-w','5',*args],check=check,capture_output=True,text=True)
existing=run('-S',CHAIN,check=False)
match=['-p','tcp','-m','conntrack','--ctorigdst',BIND,'--ctorigdstport',PORT,'--ctdir','ORIGINAL']
expected=[[*match,'-s',ip,'-j','ACCEPT'] for ip in ALLOW]+[[*match,'-j','DROP'],['-j','RETURN']]
if existing.returncode==0:
 for rule in expected:
  if run('-C',CHAIN,*rule,check=False).returncode:raise SystemExit('Existing dedicated chain differs; refusing live modification')
else:
 run('-N',CHAIN)
 for rule in expected:run('-A',CHAIN,*rule)
if run('-C','DOCKER-USER','-j',CHAIN,check=False).returncode:run('-I','DOCKER-USER','1','-j',CHAIN)
print('Dedicated firewall active; only cluster nodes/pod CIDRs allowed')
