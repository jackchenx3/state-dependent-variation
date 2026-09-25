"""Isolated 064 at-most-once Slurm adapter; uncertain states never cause resubmission."""
import fcntl,re,subprocess,sys,time,tarfile
from common import *
def normalize(state,exit_code=None):
 s=state.split()[0].rstrip('+') if state.strip() else 'UNKNOWN'
 if s=='COMPLETED':return 'COMPLETE' if exit_code=='0:0' else 'FAILED'
 if s in ('FAILED','NODE_FAIL','OUT_OF_MEMORY','BOOT_FAIL','DEADLINE','PREEMPTED','REVOKED'):return 'FAILED'
 if s in ('CANCELLED','TIMEOUT'):return s
 if s in ('PENDING','CONFIGURING','REQUEUED','REQUEUE_HOLD'):return 'PENDING'
 if s in ('RUNNING','COMPLETING','SUSPENDED','STAGE_OUT'):return 'RUNNING'
 return 'UNKNOWN'
def submit():
 with (P/'.submission.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);verify_manifest('SOURCE_SHA256SUMS')
  if (P/'submission.json').exists():return dict(read('submission.json'),reused_submission=True)
  assert not (P/'submission_attempt.json').exists(),'Uncertain previous submission; reconcile manually; NEVER retry sbatch'
  assert read('TEST_STATUS.json')['status']=='PASS';verify_references()
  save('submission_attempt.json',dict(time=time.time(),command=['sbatch','--parsable','job.sbatch']))
  r=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=str(P),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=45)
  (P/'submission.stdout').write_text(r.stdout);(P/'submission.stderr').write_text(r.stderr);assert r.returncode==0,'Submission rejected; preserve attempt'
  job=r.stdout.strip().split(';')[0];assert re.fullmatch('[0-9]+',job),'Ambiguous submission response; do not resubmit'
  v=dict(job_id=job,submitted_unix=time.time(),reused_submission=False,source_sha256=sha(P/'SOURCE_SHA256SUMS'));save('submission.json',v);return v

def parse_accounting(text,job):
 for line in text.splitlines():
  r=line.strip().split('|')
  if len(r)>=8 and r[0]==job:return dict(job_id=job,status=normalize(r[1],r[2]),slurm_state=r[1],exit_code=r[2],elapsed_seconds=r[3],cpus=r[4],requested_memory=r[5],partition=r[6],time_limit=r[7],source='sacct')
 return None

def status():
 job=read('submission.json')['job_id'];assert re.fullmatch('[0-9]+',job)
 a=subprocess.run(['sacct','-n','-X','-P','-j',job,'--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,Partition,Timelimit'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)
 if a.returncode==0:
  q=parse_accounting(a.stdout,job)
  if q:return q
 a=subprocess.run(['squeue','-h','-j',job,'-o','%i|%T'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30)
 if a.returncode==0:
  for line in a.stdout.splitlines():
   row=line.split('|')
   if len(row)==2 and row[0]==job:return dict(job_id=job,status=normalize(row[1]),slurm_state=row[1],source='squeue')
 return dict(job_id=job,status='UNKNOWN',source='scheduler_unavailable_or_accounting_pending')

def bundle():
 s=status();save('SCHEDULER_RECEIPT.json',s);assert s['status'] in ('COMPLETE','FAILED','TIMEOUT','CANCELLED')
 job=s['job_id'];a=subprocess.run(['sacct','-P','-j',job,'--units=K','--format=JobID,State,ExitCode,Elapsed,AllocCPUS,ReqMem,MaxRSS,Partition,Timelimit'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=30);assert a.returncode==0;(P/'ACCOUNTING.psv').write_text(a.stdout)
 # Preserve all newly produced files, including partial outputs on failure. Old inputs remain references.
 files=sorted(f for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts and not f.name.startswith('.') and not f.name.endswith('.tmp') and f.name not in ('REMOTE_BUNDLE_SHA256SUMS',))
 manifest=''.join(sha(f)+'  '+str(f.relative_to(P))+'\n' for f in files);(P/'REMOTE_BUNDLE_SHA256SUMS').write_text(manifest)
 dest=P.parent/'shape064-results.tar'
 with tarfile.open(str(dest),'w') as tar:
  for f in files+[P/'REMOTE_BUNDLE_SHA256SUMS']:tar.add(str(f),arcname=str(f.relative_to(P)))
 return dict(path=str(dest),sha256=sha(dest),files=len(files)+1,scheduler=s)
if __name__=='__main__':print(json.dumps({'submit':submit,'status':status,'bundle':bundle}[sys.argv[1]]()))
