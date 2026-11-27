#!/usr/bin/env python3
"""Real browser/session acceptance against an explicitly selected FlareSolverr API."""
import argparse,json,uuid,urllib.request,time
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--stage',required=True);a=p.parse_args()
base=a.url.rstrip('/')
def call(payload):
 r=urllib.request.Request(base+'/v1',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=160) as f:d=json.load(f)
 assert d.get('status')=='ok',d.get('message','API failed')
 return d
with urllib.request.urlopen(base+'/',timeout=15) as f:root=json.load(f)
assert root.get('version')=='3.5.2',root
session='migration-acceptance-'+uuid.uuid4().hex
created=False
try:
 call({'cmd':'sessions.create','session':session});created=True
 assert session in call({'cmd':'sessions.list'})['sessions']
 result=call({'cmd':'request.get','url':'https://example.com/','session':session,'maxTimeout':120000})
 solution=result['solution'];assert solution['status']==200,solution['status']
 assert 'Example Domain' in solution['response'],'Expected real browser page text'
 assert solution['url'].startswith('https://example.com'),solution['url']
 report={'stage':a.stage,'api':base,'version':root['version'],'session_create_list':True,'browser_url':solution['url'],'browser_status':solution['status'],'example_domain_rendered':True,'browser_user_agent_present':bool(solution.get('userAgent'))}
finally:
 if created:call({'cmd':'sessions.destroy','session':session})
assert session not in call({'cmd':'sessions.list'})['sessions']
report['session_destroy_list']=True
print(json.dumps(report,sort_keys=True))
