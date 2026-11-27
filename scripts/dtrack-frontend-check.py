#!/usr/bin/env python3
"""Compare exact frontend HTML/runtime config/assets; API and OIDC remain external."""
import urllib.request,urllib.parse,hashlib,json,argparse
p=argparse.ArgumentParser();p.add_argument('--destination',required=True);p.add_argument('--source',default='https://dtrack.<TU_DOMINIO>');a=p.parse_args()
source=a.source.rstrip('/');target=a.destination.rstrip('/');api='https://dtrack.<TU_DOMINIO>'
def get(url):
 r=urllib.request.urlopen(url,timeout=40);assert r.status==200;return r.read()
html=get(source+'/');dst=get(target+'/');assert html==dst,'HTML differs'
from html.parser import HTMLParser
class Assets(HTMLParser):
 def __init__(self):
  super().__init__();self.paths:set[str]=set()
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ('src','href') and value and urllib.parse.urlparse(value).path.endswith(('.js','.css')):self.paths.add(value)
parser=Assets();parser.paths=set();parser.feed(html.decode())
paths=['/static/config.json']+sorted(parser.paths)
results=[]
for path in paths:
 left=get(urllib.parse.urljoin(source+'/',path));right=get(urllib.parse.urljoin(target+'/',path));assert left==right,path
 results.append({'path':path,'bytes':len(right),'sha256':hashlib.sha256(right).hexdigest()})
config=json.loads(get(target+'/static/config.json'));assert config['API_BASE_URL']==api;discovery=json.loads(get(config['OIDC_ISSUER'].rstrip('/')+'/.well-known/openid-configuration'));assert discovery['issuer'].rstrip('/')==config['OIDC_ISSUER'].rstrip('/')
version=json.loads(get(api+'/api/version'));print(json.dumps({'source':source,'destination':target,'html_equal':True,'resources_equal':results,'api_version':version,'oidc_discovery':True,'authenticated_login_tested':False},indent=2))
