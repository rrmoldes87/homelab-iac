#!/usr/bin/env python3
"""Run on VM103 with nsenter -t <server PID> -n; localhost fixture only."""
import urllib.request,json,uuid,pathlib,time,hashlib,threading,http.server,shutil

def main():
    root=pathlib.Path('/var/lib/homelab-romifleur/data');name='migration-check-'+uuid.uuid4().hex;payload=b'HOMELAB SYNTHETIC ACCEPTANCE\n'*100
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200);self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:
        assert urllib.request.urlopen('http://127.0.0.1:8080/',timeout=30).status==200
        data=json.dumps({'id':name,'url':f'http://127.0.0.1:{server.server_port}/fixture.bin','filename':'fixture.bin','console':name}).encode();r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8080/api/download',data=data,headers={'Content-Type':'application/json'}),timeout=30);assert r.status==200
        for _ in range(100):
            files=list((root/name).rglob('fixture.bin'))
            if len(files)==1 and files[0].read_bytes()==payload:break
            time.sleep(.1)
        else:raise AssertionError('Exact fixture not downloaded')
        folders=json.load(urllib.request.urlopen('http://127.0.0.1:8080/api/folders',timeout=10));assert name in folders
        print(json.dumps({'index_http':200,'download_http':r.status,'fixture_bytes':len(payload),'fixture_sha256':hashlib.sha256(payload).hexdigest(),'folders_api_verified':True,'external_downloads':False}))
    finally:
        server.shutdown();server.server_close();t.join()
        if (root/name).exists():shutil.rmtree(root/name)
if __name__=='__main__':main()
