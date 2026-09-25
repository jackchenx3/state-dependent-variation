"""Seal checked064 delivery and verify its HPC copy. Never publish a success for blocked execution."""
import subprocess,tarfile,shlex,datetime
from common import *
from live064 import HOST,REMOTE,SSH,PY

def main():
 assert read('LIVE_RESULT.json')['status']=='COMPLETE' and read('VALIDATION_CHECK.json')['status']=='PASS' and read('AUDIT_CHECK.json')['status']=='PASS'
 assert read('VISUAL_QA.json')['status']=='PASS' and read('VISUAL_QA.json')['png_count']==2
 verify_manifest('SOURCE_SHA256SUMS');verify_manifest('RESULT_SHA256SUMS');verify_references()
 assert (P/'REPORT.md').exists() and len(list(P.glob('*.png')))==2
 # A sealed delivery is resumed verbatim; no status refresh mutates it.
 if not (P/'DELIVERY_SHA256SUMS').exists():
  current_size=package_bytes();assert current_size<=512*1024*1024
  save('FINAL_SIZE_CHECK.json',dict(status='PASS',bytes_before_seal=current_size,limit_bytes=512*1024*1024,scope='Finite package including source/science/report/logs, excluding archives stored outside it'))
  save('FINAL_STATUS.json',dict(status='EXECUTION_COMPLETE_REVIEW_PENDING',task_id='ORG-STATE-SHAPE-064',revision=1,job_id=read('COMPLETION.json')['job_id'],source_sha256=sha(P/'SOURCE_SHA256SUMS'),result_sha256=sha(P/'RESULT_SHA256SUMS'),primary=read('VALIDATION_CHECK.json')['primary_estimate'],new_paths=12288,stored_controls=12288,outcomes=380,scientific_status=read('VALIDATION_CHECK.json')['scientific_status'],main_figures=2,next_variant_authorized=False,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
  files=sorted(f for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts and not f.name.startswith('.') and not f.name.endswith('.tmp') and f.name not in ('EXECUTOR_STATUS.json','ACCESS_STATUS.json','DELIVERY_RECEIPT.json','DELIVERY_SHA256SUMS'))
  (P/'DELIVERY_SHA256SUMS').write_text(''.join(sha(f)+'  '+str(f.relative_to(P))+'\n' for f in files))
 verify_manifest('DELIVERY_SHA256SUMS');assert package_bytes()<=512*1024*1024
 names=[x.split('  ',1)[1] for x in (P/'DELIVERY_SHA256SUMS').read_text().splitlines()]+['DELIVERY_SHA256SUMS'];existing={x.split('  ',1)[1] for x in (P/'REMOTE_BUNDLE_SHA256SUMS').read_text().splitlines()};archive=P.parent/'shape064-delivery.tar'
 with tarfile.open(str(archive),'w') as t:
  for n in names:
   if n not in existing:t.add(str(P/n),arcname=n)
 remote_archive=REMOTE+'/../shape064-delivery.tar';subprocess.run(['scp','-q',str(archive),HOST+':'+remote_archive],check=True,timeout=300)
 script='''import sys,pathlib,tarfile,hashlib,json
root=pathlib.Path(sys.argv[1])
with tarfile.open(sys.argv[2]) as t:
 for m in t.getmembers():
  p=pathlib.PurePosixPath(m.name)
  if p.is_absolute() or '..' in p.parts or not m.isfile():raise ValueError('unsafe delivery entry')
  data=t.extractfile(m).read();f=root/str(p)
  if f.exists() and f.read_bytes()!=data:raise ValueError('existing file differs: '+str(p))
  if not f.exists():
   f.parent.mkdir(parents=True,exist_ok=True)
   with f.open('xb') as out:out.write(data)
n=0
for line in (root/'DELIVERY_SHA256SUMS').read_text().splitlines():
 h,name=line.split('  ',1);dig=hashlib.sha256()
 with (root/name).open('rb') as src:
  for b in iter(lambda:src.read(1048576),b''):dig.update(b)
 if dig.hexdigest()!=h:raise ValueError('delivery hash mismatch: '+name)
 n+=1
print(json.dumps({'verified_files':n,'delivery_sha256':hashlib.sha256((root/'DELIVERY_SHA256SUMS').read_bytes()).hexdigest()}))
'''
 r=subprocess.run(SSH+[' '.join(shlex.quote(x) for x in [PY,'-E','-s','-S','-B','-c',script,REMOTE,remote_archive])],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300);assert r.returncode==0,r.stderr.decode();verification=json.loads(r.stdout);assert verification['delivery_sha256']==sha(P/'DELIVERY_SHA256SUMS')
 receipt=dict(read('FINAL_STATUS.json'),state='SUBMITTED',execution_state='COMPLETE_LOCAL_AND_HPC_VERIFIED',delivery=verification,package=str(P),hpc_path=REMOTE)
 f=P/'DELIVERY_RECEIPT.json';f.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
