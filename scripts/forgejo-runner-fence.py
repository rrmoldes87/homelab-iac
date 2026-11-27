#!/usr/bin/python3
import subprocess
name='hm_forgejo_runner_fence'
exists=subprocess.run(['nft','list','table','inet',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
spec=('delete table inet '+name+'\n' if exists else '')+'table inet hm_forgejo_runner_fence {\n chain guard {\n  type filter hook forward priority -10; policy accept;\n  ip saddr { 192.168.1.206, 10.244.5.249 } meta l4proto tcp ct direction original ct original ip daddr 192.168.1.92 ct original proto-dst { 18116, 18117 } counter drop\n }\n}\n'
subprocess.run(['nft','-c','-f','-'],input=spec,text=True,check=True)
subprocess.run(['nft','-f','-'],input=spec,text=True,check=True)
subprocess.run(['nft','list','table','inet',name],check=True)
