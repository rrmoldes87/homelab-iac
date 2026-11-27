#!/usr/bin/env python3
"""Bounded VM103 local read-only native health checks. No secrets or payloads exported."""
import concurrent.futures,json,time,urllib.request
PROBES={'qdrant':(18100,'/healthz'),'nextcloud':(18111,'/status.php'),'forgejo':(18116,'/api/healthz'),'grafana':(18300,'/api/health'),'jellyfin':('192.168.1.99',8096,'/health'),'actual':(18107,'/health'),'tei':(18115,'/health'),'ntfy':(18080,'/v1/health'),'homebox':(18088,'/api/v1/status')}
def healthy(service,status,body):
 if status!=200:return False
 try:
  if service=='nextcloud':
   d=json.loads(body);return d.get('installed') is True and d.get('maintenance') is False and d.get('needsDbUpgrade') is False
  if service=='forgejo':return json.loads(body).get('status')=='pass'
  if service=='grafana':return json.loads(body).get('database')=='ok'
  if service=='actual':return json.loads(body).get('status')=='UP'
  if service=='ntfy':return json.loads(body).get('healthy') is True
  if service=='homebox':return json.loads(body).get('health') is True
  if service=='qdrant':return body.strip()=='healthz check passed'
  if service=='jellyfin':return body.strip()=='Healthy'
  if service=='mlflow':return body.strip()=='OK'
  if service=='tei':return body.strip()==''
 except (ValueError,TypeError,AttributeError):return False
 return False

def probe(service):
 spec=PROBES[service]
 host,port,path=(spec if len(spec)==3 else ('192.168.1.92',spec[0],spec[1]));start=time.monotonic();ok=False;status=0
 try:
  with urllib.request.urlopen('http://'+host+':'+str(port)+path,timeout=8) as r:
   status=r.status;ok=healthy(service,status,r.read(16384).decode())
 except Exception:pass
 return {'service':service,'healthy':ok,'http_status':status,'duration':time.monotonic()-start}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:print(json.dumps(list(pool.map(probe,PROBES))))
