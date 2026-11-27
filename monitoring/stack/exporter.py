#!/usr/bin/env python3
"""Bounded, read-only aggregate exporter. Never reads messages/prompts or exports identities."""
import concurrent.futures,hashlib,http.client,http.server,json,os,pathlib,shlex,sqlite3,ssl,subprocess,threading,time,urllib.request,base64
HOME=pathlib.Path('/home/<TU_USUARIO>'); PRIVATE=HOME/'.config/homelab-monitoring'; KEY=HOME/'.ssh/proxmox_homelab_ed25519'
SSH=['ssh','-i',str(KEY),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=8']
def run(cmd):return subprocess.check_output(cmd,text=True,timeout=80)
def remote(ip,cmd):return run(SSH+['root@'+ip,cmd])
def env(path):return {k:v.strip().strip('"').strip("'") for k,v in (x.removeprefix('export ').split('=',1) for x in pathlib.Path(path).read_text().splitlines() if '=' in x and not x.lstrip().startswith('#'))}
def metric(name,value,**labels):
 value=float(value)
 if not __import__('math').isfinite(value):raise ValueError('nonfinite')
 return name+('{'+','.join(k+'='+json.dumps(str(v)) for k,v in sorted(labels.items()))+'}' if labels else '')+' '+str(value)+'\n'
def ha():
 e=env(HOME/'.hermes/.env'); headers={'Authorization':'Bearer '+e['HASS_TOKEN']}
 with urllib.request.urlopen(urllib.request.Request(e['HASS_URL']+'/api/states',headers=headers),timeout=15) as r: states=json.load(r)
 counts={}
 for x in states:
  domain=x['entity_id'].split('.')[0]
  if domain not in {'sensor','binary_sensor','light','switch','automation','script','device_tracker','person','climate','media_player','update','zone','button','number','select','sun','weather','event','calendar','todo'}:domain='other'
  status=x['state'] if x['state'] in ('unavailable','unknown') else 'available'
  counts[domain,status]=counts.get((domain,status),0)+1
 out=''.join(metric('homelab_ha_entities',v,domain=d,status=s) for (d,s),v in counts.items())
 # Only infrastructure sensors; no presence, location, names or household devices.
 allowed={'temperature','power','energy','voltage','current','frequency','data_size','data_rate'}
 selected=0
 for x in states:
  entity=x['entity_id']; attrs=x.get('attributes',{}); dc=attrs.get('device_class','')
  if not entity.startswith('sensor.') or not any(k in entity for k in ('proxmox','truenas','ups_','opnsense','processor_','memory_','disk_')) or dc not in allowed:continue
  try:value=float(x['state'])
  except (ValueError,TypeError):continue
  if not __import__('math').isfinite(value):continue
  out+=metric('homelab_ha_infrastructure_sensor',value,sensor=entity,device_class=dc,unit=attrs.get('unit_of_measurement',''));selected+=1
 return out+metric('homelab_ha_infrastructure_selected_sensors',selected)
def hermes():
 with sqlite3.connect('file:'+str(HOME/'.hermes/state.db')+'?mode=ro',uri=True,timeout=5) as c:
  fields=['input_tokens','output_tokens','cache_read_tokens','cache_write_tokens','reasoning_tokens','tool_call_count','api_call_count']
  row=c.execute('select count(*),'+','.join('coalesce(sum('+f+'),0)' for f in fields)+' from sessions').fetchone()
  out=metric('homelab_hermes_sessions',row[0])+''.join(metric('homelab_hermes_usage',v,kind=f) for f,v in zip(fields,row[1:]))
  for status,n in c.execute("select coalesce(cost_status,'unknown'),count(*) from sessions group by cost_status"):
   out+=metric('homelab_hermes_cost_sessions',n,status=status if status in ('included','unknown','estimated','actual','free') else 'other')
  for kind in ['estimated','actual']:
   n,v=c.execute('select count('+kind+'_cost_usd),sum('+kind+'_cost_usd) from sessions').fetchone();out+=metric('homelab_hermes_cost_records',n,kind=kind)
   if n:out+=metric('homelab_hermes_recorded_cost_usd',v,kind=kind)
  return out

def opn_request(path):
 e=env(HOME/'.config/homelab-credentials/opnsense-api.env'); ctx=ssl._create_unverified_context(); conn=http.client.HTTPSConnection('192.168.1.1',timeout=12,context=ctx);conn.connect()
 pin=(PRIVATE/'opnsense.sha256').read_text().strip()
 if hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest()!=pin:raise ValueError('TLS pin changed')
 auth=base64.b64encode((e['key']+':'+e['secret']).encode()).decode();conn.request('GET',path,headers={'Authorization':'Basic '+auth});r=conn.getresponse()
 if r.status!=200:raise ValueError('API unavailable')
 d=json.loads(r.read());conn.close();return d

def opn():
 r=opn_request('/api/diagnostics/system/systemResources')['memory'];out=metric('homelab_opnsense_memory_bytes',r['total'],kind='total')+metric('homelab_opnsense_memory_bytes',r['used'],kind='used')
 t=opn_request('/api/diagnostics/system/systemTime');out+=metric('homelab_opnsense_load1',t['loadavg'].split(',')[0])
 rows=opn_request('/api/diagnostics/interface/getInterfaceStatistics')['statistics'];seen=set()
 for _,r in rows.items():
  name=r['name']
  # The link-layer row is authoritative; skip IP-address duplicate counters.
  if name in seen or ('mtu' not in r and name!='pppoe0'):continue
  seen.add(name)
  for field,direction in [('received-bytes','rx'),('sent-bytes','tx')]:
   if field in r:out+=metric('homelab_opnsense_interface_bytes_total',r[field],interface=name,direction=direction)
 return out

def proxmox():
 rows=json.loads(remote('192.168.1.221','pvesh get /cluster/resources --output-format json'));out=''
 for r in rows:
  kind=r['type'];labels={'node':r.get('node','unknown'),'resource':r['id'],'type':kind}
  if kind not in ('node','qemu','lxc','storage'):continue
  out+=metric('homelab_pve_running',r.get('status') in ('running','online','available'),**labels)
  for k in ['cpu','mem','maxmem','disk','maxdisk','uptime']:
   if k in r:out+=metric('homelab_pve_'+k,r[k],**labels)
 return out

def docker():
 code="import subprocess,json; rows=[json.loads(x) for x in subprocess.check_output(['docker','stats','--no-stream','--format','{{json .}}'],text=True).splitlines()];print(json.dumps(rows))"
 command='qm guest exec 103 --timeout 90 -- python3 -c '+shlex.quote(code)
 result=json.loads(remote('192.168.1.221',command))
 if result.get('exitcode',0):raise ValueError('guest collection failed')
 rows=json.loads(result['out-data']);out=metric('homelab_docker_running_containers',len(rows))
 for r in rows:
  name=r['Name'];out+=metric('homelab_docker_cpu_percent',r['CPUPerc'].rstrip('%'),container=name)
  out+=metric('homelab_docker_memory_percent',r['MemPerc'].rstrip('%'),container=name)
  out+=metric('homelab_docker_processes',r['PIDs'],container=name)
 return out

DOCKER_HOSTS={'vm103':('192.168.1.221','qemu',103),'vm107':('192.168.1.200','qemu',107),'ct141':('192.168.1.210','lxc',141),'ct145':('192.168.1.210','lxc',145),'ct146':('192.168.1.221','lxc',146),'ct147':('192.168.1.221','lxc',147),'ct148':('192.168.1.221','lxc',148),'ct151':('192.168.1.210','lxc',151),'ct152':('192.168.1.200','lxc',152),'ct153':('192.168.1.210','lxc',153),'ct154':('192.168.1.200','lxc',154)}
def docker_inventory_metrics(rows,host):
 out=''
 for r in rows:
  labels={'host':host,'container':r['name']}
  out+=metric('homelab_docker_container_running',r['running'],**labels)+metric('homelab_docker_container_restarts',r['restarts'],**labels)
  if r['health'] in ('healthy','unhealthy','starting'):out+=metric('homelab_docker_container_health',1,status=r['health'],**labels)
 return out

def docker_host(host):
 ip,kind,vmid=DOCKER_HOSTS[host]
 # Format only permitted state fields; never return Docker environment/secrets.
 probe="ids=$(docker ps -aq); if [ -n \"$ids\" ]; then docker inspect --format '{{.Name}}|{{.State.Running}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}|{{.RestartCount}}' $ids; fi"
 command=('pct exec '+str(vmid)+' -- sh -c '+shlex.quote(probe)) if kind=='lxc' else ('qm guest exec '+str(vmid)+' --timeout 30 -- sh -c '+shlex.quote(probe))
 raw=remote(ip,command)
 if kind=='qemu':
  result=json.loads(raw)
  if result.get('exitcode',0):raise ValueError('guest inventory failed')
  raw=result.get('out-data','')
 rows=[]
 for line in raw.splitlines():
  name,running,health,restarts=line.split('|');rows.append({'name':name.lstrip('/'),'running':running=='true','health':health,'restarts':int(restarts)})
 return docker_inventory_metrics(rows,host)

def storage():
 import sys
 sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1])); import monitor
 samples=monitor.collect({'nodes':['192.168.1.200','192.168.1.210','192.168.1.221'],'ssh_key':str(KEY)});out=''
 for node,s in samples.items():
  out+=metric('homelab_storage_collection_errors',len(s.get('errors',[])),node=node)
  for r in s.get('thin',[]):
   for kind in ['data','metadata']:out+=metric('homelab_thin_usage_percent',r[kind],node=node,pool=r['pool'],kind=kind)
  for r in s.get('zfs',[]):out+=metric('homelab_zfs_capacity_percent',r['capacity'],node=node,pool=r['pool'])+metric('homelab_zfs_healthy',r['health']=='ONLINE',node=node,pool=r['pool'])
  for r in s.get('disks',[]):out+=metric('homelab_smart_healthy',r['healthy'],node=node,device=r['device'])
 return out
def litellm():
 code="import pathlib,json,re; t=pathlib.Path('/app/config.yaml').read_text(); print(json.dumps({'retired_backend_referenced':int('192.168.1.75' in t),'configured_models':len(re.findall(r'model_name:',t))}))"
 result=json.loads(remote('192.168.1.221','qm guest exec 103 --timeout 20 -- docker exec homelab-litellm-web-1 python -c '+shlex.quote(code)))
 if result.get('exitcode',0):raise ValueError('LiteLLM inspection failed')
 return ''.join(metric('homelab_litellm_'+k,v) for k,v in json.loads(result['out-data']).items())

def openwebui():
 code="import sqlite3,json; c=sqlite3.connect('file:/opt/open-webui/data/webui.db?mode=ro',uri=True,timeout=5); print(json.dumps(dict(c.execute('select count(*),coalesce(max(updated_at),0) from chat').fetchone() and zip(['chats','last_activity_timestamp_seconds'],c.execute('select count(*),coalesce(max(updated_at),0) from chat').fetchone()))))"
 raw=remote('192.168.1.221','pct exec 144 -- python3 -c '+shlex.quote(code))
 return ''.join(metric('homelab_openwebui_'+k,v) for k,v in json.loads(raw).items())

def backup_expectations(jobs,resources):
 # ID alone is not an identity: historical ct/103 and current vm/103 coexist.
 ids=set()
 for job in jobs:
  if job.get('enabled') and job.get('storage')=='PBS-Truenas' and job.get('schedule')=='03:00':
   ids.update(str(job.get('vmid','')).split(','))
 return ''.join(metric('homelab_pbs_expected_daily_backup',1,guest_id=str(r['vmid']),type={'qemu':'vm','lxc':'ct'}[r['type']]) for r in resources if str(r.get('vmid')) in ids and not r.get('template') and r.get('type') in ('qemu','lxc'))

def pbs():
 prefix='pct exec 113 -- proxmox-backup-manager '
 tasks=json.loads(remote('192.168.1.210',prefix+'task list --all true --limit 100 --output-format json'))
 jobs=json.loads(remote('192.168.1.210',prefix+'verify-job list --output-format json'))
 stores=json.loads(remote('192.168.1.210',prefix+'datastore list --output-format json'))
 out=metric('homelab_pbs_verify_jobs',len(jobs))+metric('homelab_pbs_datastores',len(stores))
 for store in stores:
  name=store['name'];base='pct exec 113 -- proxmox-backup-debug api get /admin/datastore/'+name
  status=json.loads(remote('192.168.1.210',base+'/status --output-format json'))
  groups=json.loads(remote('192.168.1.210',base+'/groups --output-format json'))
  for key in ('avail','used','total'):out+=metric('homelab_pbs_datastore_bytes',status[key],datastore=name,kind=key)
  for group in groups:
   # No owners, paths, names or contents; VM identifiers are infrastructure labels.
   labels={'datastore':name,'guest_id':group['backup-id'],'type':group['backup-type']}
   out+=metric('homelab_pbs_group_last_backup_timestamp_seconds',group['last-backup'],**labels)+metric('homelab_pbs_group_snapshots',group['backup-count'],**labels)
 daily_jobs=json.loads(remote('192.168.1.200','pvesh get /cluster/backup --output-format json'))
 resources=json.loads(remote('192.168.1.200','pvesh get /cluster/resources --type vm --output-format json'))
 out+=backup_expectations(daily_jobs,resources)
 for kind in ('backup','verify','garbage_collection'):
  rows=[r for r in tasks if r.get('worker_type')==kind and r.get('endtime')]
  out+=metric('homelab_pbs_recent_tasks',len(rows),kind=kind)
  if rows:
   row=max(rows,key=lambda r:r['endtime']);out+=metric('homelab_pbs_last_task_timestamp_seconds',row['endtime'],kind=kind)+metric('homelab_pbs_last_task_success',row.get('status')=='OK',kind=kind)
 return out

def truenas_request(path):
 # Per-host pinned TLS: reject a changed certificate before sending credentials.
 conn=http.client.HTTPSConnection('192.168.1.157',timeout=15,context=ssl._create_unverified_context());conn.connect()
 try:
  if hashlib.sha256(conn.sock.getpeercert(binary_form=True)).hexdigest()!=(PRIVATE/'truenas.sha256').read_text().strip():raise ValueError('TLS pin changed')
  key=(HOME/'.config/homelab-credentials/truenas-api-key').read_text().strip()
  conn.request('GET','/api/v2.0/'+path,headers={'Authorization':'Bearer '+key});r=conn.getresponse()
  if r.status!=200:raise ValueError('TrueNAS API unavailable')
  return json.loads(r.read())
 finally:conn.close()

def truenas_metrics(data):
 out=''
 for p in data['pool']:
  labels={'pool_id':str(p['id'])}
  out+=metric('homelab_truenas_pool_healthy',p['healthy'],**labels)
  for field in ('size','allocated','free'):out+=metric('homelab_truenas_pool_bytes',p[field],kind=field,**labels)
  out+=metric('homelab_truenas_pool_usage_percent',100*p['allocated']/p['size'],**labels)
 out+=metric('homelab_truenas_disks',len(data['disk']))
 out+=metric('homelab_truenas_smart_disks',sum(bool(d.get('togglesmart')) for d in data['disk']),kind='enabled')
 for value,label in ((True,'supported'),(False,'unsupported'),(None,'unknown')):out+=metric('homelab_truenas_smart_disks',sum(d.get('supports_smart') is value for d in data['disk']),kind=label)
 rows=data['smart/test/results']
 out+=metric('homelab_truenas_smart_disks_with_results',sum(bool(d.get('tests')) for d in rows))
 for status in ('SUCCESS','ABORTED','FAILED','UNKNOWN'):
  out+=metric('homelab_truenas_smart_latest_test_disks',sum((str(d['tests'][0].get('status')) if d['tests'][0].get('status') in ('SUCCESS','ABORTED','FAILED') else 'UNKNOWN')==status for d in rows if d.get('tests')),status=status)
 # SMART capability/configuration is not a health verdict; only latest logged test per disk.
 for p in data['pool']:
  scan=p.get('scan') or {}
  if scan.get('errors') is not None:out+=metric('homelab_truenas_scan_errors',scan['errors'],pool_id=p['id'])
  if isinstance(scan.get('end_time'),dict):out+=metric('homelab_truenas_scan_end_timestamp_seconds',scan['end_time']['$date']/1000,pool_id=p['id'])
 out+=metric('homelab_truenas_alerts_dismissed',sum(bool(a.get('dismissed')) for a in data['alert/list']))
 for level in ('INFO','NOTICE','WARNING','ERROR','CRITICAL','ALERT','EMERGENCY','other'):
  out+=metric('homelab_truenas_alerts',sum(not a.get('dismissed',False) and (a.get('level')==level if level!='other' else a.get('level') not in ('INFO','NOTICE','WARNING','ERROR','CRITICAL','ALERT','EMERGENCY')) for a in data['alert/list']),level=level)
 for endpoint,kind in [('replication','replication'),('pool/snapshottask','snapshot'),('cloudsync','cloudsync'),('smart/test','smart_test'),('pool/scrub','scrub'),('rsynctask','rsync')]:
  rows=data[endpoint];out+=metric('homelab_truenas_tasks',len(rows),kind=kind)
  if kind!='smart_test':out+=metric('homelab_truenas_tasks_enabled',sum(bool(r.get('enabled')) for r in rows),kind=kind)
  if kind=='snapshot':
   for row in rows:
    state=row.get('state') or {};out+=metric('homelab_truenas_snapshot_task_success',state.get('state')=='FINISHED',task_id=row['id'])
    if isinstance(state.get('datetime'),dict):out+=metric('homelab_truenas_snapshot_task_timestamp_seconds',state['datetime']['$date']/1000,task_id=row['id'])
 return out

def truenas():
 return truenas_metrics({p:truenas_request(p) for p in ('pool','disk','alert/list','replication','pool/snapshottask','cloudsync','smart/test','smart/test/results','pool/scrub','rsynctask')})

def native_apps():
 code=pathlib.Path(__file__).with_name('native_health.py').read_text()
 result=json.loads(remote('192.168.1.221','qm guest exec 103 --timeout 30 -- python3 -c '+shlex.quote(code)))
 if result.get('exitcode',0):raise ValueError('native health probe failed')
 rows=json.loads(result['out-data'])
 return ''.join(metric('homelab_app_native_health',r['healthy'],host='vm103',service=r['service'])+metric('homelab_app_native_http_status',r['http_status'],host='vm103',service=r['service'])+metric('homelab_app_native_probe_duration_seconds',r['duration'],host='vm103',service=r['service']) for r in rows)

SOURCES={'native_apps':native_apps,'truenas':truenas,'pbs':pbs,'openwebui':openwebui,'homeassistant':ha,'hermes':hermes,'opnsense':opn,'proxmox':proxmox,'docker':docker,'storage':storage}
SOURCES.update({'docker_'+host:(lambda host=host:docker_host(host)) for host in DOCKER_HOSTS})
CACHE={};LOCK=threading.Lock()
def collect_one(name,fn):
 try:
  data=fn();now=time.time()
  with LOCK:CACHE[name]=(data,1,now)
 except Exception:
  with LOCK:
   # Do not serve stale data as a current successful observation.
   CACHE[name]=('',0,CACHE.get(name,('',0,0))[2])
def loop():
 while True:
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(lambda item:collect_one(*item),SOURCES.items()))
  time.sleep(60)
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path!='/metrics':self.send_error(404);return
  with LOCK:
   text=''.join(data+metric('homelab_collection_success',ok,source=name)+metric('homelab_collection_timestamp_seconds',stamp,source=name) for name,(data,ok,stamp) in CACHE.items())
  body=text.encode();self.send_response(200);self.send_header('Content-Type','text/plain; version=0.0.4');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*a):pass
if __name__=='__main__':
 threading.Thread(target=loop,daemon=True).start();http.server.ThreadingHTTPServer(('192.168.1.155',9810),Handler).serve_forever()
