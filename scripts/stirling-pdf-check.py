#!/usr/bin/env python3
"""Exercise StirlingPDF using generated, non-personal PDF fixtures (stdlib only)."""
import argparse,urllib.request,uuid,json,re

def fixture():
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>',b'<< /Length 0 >>\nstream\n\nendstream']
    data=b'%PDF-1.4\n';offsets=[0]
    for n,obj in enumerate(objects,1):offsets.append(len(data));data+=f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref=len(data);data+=b'xref\n0 5\n0000000000 65535 f \n'+b''.join(f'{x:010d} 00000 n \n'.encode() for x in offsets[1:]);return data+f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()

def check(base):
    page=urllib.request.urlopen(base+'/',timeout=60);assert page.status==200
    boundary='migration-'+uuid.uuid4().hex;chunks=[]
    for name in ['one.pdf','two.pdf']:
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="fileInput"; filename="{name}"\r\nContent-Type: application/pdf\r\n\r\n'.encode()+fixture()+b'\r\n')
    chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="sortType"\r\n\r\norderProvided\r\n--{boundary}--\r\n'.encode())
    req=urllib.request.Request(base+'/api/v1/general/merge-pdfs',data=b''.join(chunks),headers={'Content-Type':'multipart/form-data; boundary='+boundary})
    r=urllib.request.urlopen(req,timeout=120);pdf=r.read();assert r.status==200 and pdf.startswith(b'%PDF-'),(r.status,pdf[:100]);pages=len(re.findall(rb'/Type\s*/Page\b',pdf));assert pages==2,('Expected two page objects',pages)
    return {'base':base,'index_http':page.status,'merge_http':r.status,'merged_pages':pages,'output_bytes':len(pdf),'synthetic_fixture_only':True}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();print(json.dumps(check(a.destination.rstrip('/')),indent=2))
