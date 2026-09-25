"""064-only deterministic staging/submission/poll/retrieval. No AI calls or recurring task."""
import argparse,base64,fcntl,subprocess,shlex,time,tarfile,hashlib
from common import *
HOST='chenx3@batch.ncifcrf.gov';REMOTE='__HPC_PROJECT__/experiments/population_shape_v1';PY='/usr/bin/python3';SSH=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',HOST]
STAGE='''import sys,json,base64,hashlib,pathlib,fcntl
p=json.load(sys.stdin);root=pathlib.Path(p['directory']);root.mkdir(parents=True,exist_ok=True)
with (root/'.stage.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for n,x in p['files'].items():
  if pathlib.Path(n).name!=n:raise ValueError('unsafe payload name')
  data=base64.b64decode(x['base64']);f=root/n
  if hashlib.sha256(data).hexdigest()!=x['sha256']:raise ValueError('bad payload hash')
  if f.exists() and f.read_bytes()!=data:raise ValueError('frozen payload differs: '+n)
  if not f.exists():
   with f.open('xb') as out:out.write(data)
print(json.dumps({'staged':True,'files':len(p['files'])}))
'''
def remote(args,data=None,timeout=180):
 r=subprocess.run(SSH+[' '.join(shlex.quote(x) for x in args)],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if r.returncode:
  (P/'last_transport_error.log').write_bytes(r.stderr);raise RuntimeError('SSH/remote failure; see last_transport_error.log')
 return json.loads(r.stdout)
def retrieve(bundle):
 dest=P.parent/'shape064-retrieved.tar';r=subprocess.run(['scp','-q',HOST+':'+bundle['path'],str(dest)],timeout=600);assert r.returncode==0 and sha(dest)==bundle['sha256']
 with tarfile.open(str(dest),'r') as t:
  for member in t.getmembers():
   n=pathlib.PurePosixPath(member.name);assert not n.is_absolute() and '..' not in n.parts and member.isfile(),'Unsafe archive entry'
   data=t.extractfile(member).read();target=P/str(n)
   if target.exists():assert target.read_bytes()==data,'Existing local artifact differs: '+str(n)
   else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 verify_manifest('REMOTE_BUNDLE_SHA256SUMS');save('RETRIEVAL_CHECK.json',dict(status='PASS',bundle_sha256=bundle['sha256'],files=bundle['files']))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--wait-seconds',type=int,default=900);args=ap.parse_args();assert 1<=args.wait_seconds<=1800
 verify_manifest('SOURCE_SHA256SUMS')
 if (P/'LIVE_RESULT.json').exists() and read('LIVE_RESULT.json')['status']=='COMPLETE':
  verify_manifest('REMOTE_BUNDLE_SHA256SUMS');print(json.dumps(dict(read('LIVE_RESULT.json'),reused_completed_delivery=True)),flush=True);return
 names=[line.split('  ',1)[1] for line in (P/'SOURCE_SHA256SUMS').read_text().splitlines()]+['SOURCE_SHA256SUMS']
 payload={n:dict(sha256=sha(P/n),base64=base64.b64encode((P/n).read_bytes()).decode()) for n in names}
 print(json.dumps(remote([PY,'-E','-s','-S','-B','-c',STAGE],json.dumps(dict(directory=REMOTE,files=payload)).encode())),flush=True)
 sub=remote([PY,'-E','-s','-S','-B',REMOTE+'/hpc_control.py','submit']);save('LOCAL_SUBMISSION.json',sub);print(json.dumps(sub),flush=True)
 start=time.monotonic();fails=0;last=None;polls=0
 while True:
  polls+=1
  try:s=remote([PY,'-E','-s','-S','-B',REMOTE+'/hpc_control.py','status'],timeout=70);fails=0
  except (RuntimeError,subprocess.TimeoutExpired,json.JSONDecodeError):fails+=1;s=dict(status='UNKNOWN',job_id=sub['job_id'],source='transport_failure')
  save('LOCAL_SCHEDULER.json',s)
  if s['status']!=last:print(json.dumps(s),flush=True);last=s['status']
  if s['status'] in ('COMPLETE','FAILED','TIMEOUT','CANCELLED'):break
  if fails>=3 or time.monotonic()-start>=args.wait_seconds:raise SystemExit('Bounded monitoring paused; do not resubmit or cancel; resume same adapter')
  time.sleep(min(15,max(.1,args.wait_seconds-(time.monotonic()-start))))
 bundle=remote([PY,'-E','-s','-S','-B',REMOTE+'/hpc_control.py','bundle'],timeout=300);retrieve(bundle)
 ok=s['status']=='COMPLETE' and (P/'VALIDATION_CHECK.json').exists() and read('VALIDATION_CHECK.json')['status']=='PASS' and (P/'COMPLETION.json').exists() and read('COMPLETION.json')['job_id']==sub['job_id'] and (P/'AUDIT_CHECK.json').exists() and read('AUDIT_CHECK.json')['status']=='PASS'
 event=dict(task_id='ORG-STATE-SHAPE-064',job_id=sub['job_id'],status='COMPLETE' if ok else 'FAILED',source_sha256=sha(P/'SOURCE_SHA256SUMS'),new_paths=read('PRODUCTION_RUNTIME.json')['new_paths'] if (P/'PRODUCTION_RUNTIME.json').exists() else None,scientific_status=read('VALIDATION_CHECK.json').get('scientific_status') if (P/'VALIDATION_CHECK.json').exists() else None,controller_model_calls=0,actual_credit_savings=None)
 h=hashlib.sha256(json.dumps(event,sort_keys=True).encode()).hexdigest();f=P/('event-'+h+'.json')
 if not f.exists():save(f.name,event)
 save('LIVE_RESULT.json',dict(event,scheduler_polls=polls,reused_submission=sub['reused_submission'],event_path=f.name));print(json.dumps(event),flush=True)
 if not ok:raise SystemExit(1)
if __name__=='__main__':
 with (P/'.monitor.lock').open('a') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
