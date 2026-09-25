"""Allocation-only runner; monitor failures propagate and preserve partial records."""
import os,sys,json,time,pathlib,subprocess,threading,traceback
from io_utils import sha,save,telemetry,ADVICE
P=pathlib.Path(__file__).resolve().parent
GUARD=3758096384
class Guard:
 def __init__(self):self.stop=threading.Event();self.error=None
 def fail(self,error):
  self.error=dict(time=time.time(),error=str(error),traceback=traceback.format_exc(),partial_outputs_preserved=True)
  try:save('MONITOR_FAILURE.json',self.error)
  finally:self.stop.set()
 def check(self):
  if self.error:raise RuntimeError('Monitor failed: '+self.error['error'])
  if self.stop.is_set():raise RuntimeError('Monitor requested stop; partial outputs preserved')
def cgpaths():
 paths=[]
 for line in pathlib.Path('/proc/self/cgroup').read_text().splitlines():
  _,controllers,path=line.split(':',2)
  if 'memory' in controllers.split(','):paths.append(pathlib.Path('/sys/fs/cgroup/memory')/path.lstrip('/'))
  if controllers=='':paths.append(pathlib.Path('/sys/fs/cgroup')/path.lstrip('/'))
 return paths
def monitor_body(guard):
 paths=cgpaths()
 with open('MEMORY_TELEMETRY.jsonl','w') as out:
  while not guard.stop.is_set():
   q=telemetry('allocation-monitor');q['cgroup_paths']=[str(p) for p in paths];q['cgroups']=[];current=[]
   for p in paths:
    stats={}
    for name in ('memory.current','memory.peak','memory.max','memory.usage_in_bytes','memory.max_usage_in_bytes','memory.limit_in_bytes','memory.stat'):
     f=p/name
     if f.is_file():stats[name]=f.read_text().strip()
    q['cgroups'].append(stats)
    for k in ('memory.current','memory.usage_in_bytes'):
     if k in stats:
      observed=int(stats[k]);current.append(observed)
      if observed>=GUARD:
       save('RESOURCE_STOP.json',dict(time=time.time(),observed=observed,threshold=GUARD,counter=k,partial_outputs_preserved=True));guard.stop.set()
   q['current_counter_available']=bool(current);out.write(json.dumps(q,separators=(',',':'))+'\n');out.flush()
   if not current:raise RuntimeError('No readable current cgroup memory counter; conservative stop')
   guard.stop.wait(1.)
def monitor(guard,body=monitor_body):
 try:body(guard)
 except BaseException as error:guard.fail(error)
def stage(script,log,guard):
 guard.check();start=time.time()
 with open(log,'w') as out:
  p=subprocess.Popen([sys.executable,'-E','-s','-S','-B',script],stdout=out,stderr=subprocess.STDOUT)
  try:
   while p.poll() is None:
    if guard.stop.wait(.2):guard.check()
   guard.check()
   if p.returncode:raise RuntimeError(script+' failed exit '+str(p.returncode))
  except BaseException:
   if p.poll() is None:
    p.terminate()
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:p.kill();p.wait()
   raise
 return dict(script=script,elapsed_seconds=time.time()-start,exit_code=p.returncode)
def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('RUN_STARTED.json').exists();start=time.time();save('RUN_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,python=sys.version));guard=Guard();t=threading.Thread(target=monitor,args=(guard,),daemon=True);t.start();stages=[];success=False
 try:
  for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():h,f=line.split(None,1);assert sha(f)==h;guard.check()
  stages.append(stage('test_model.py','tests.log',guard));save('TEST_STATUS.json',dict(status='PASS',stage=stages[-1],tests_log_sha256=sha('tests.log')))
  stages.append(stage('make_inputs.py','inputs.log',guard));stages.append(stage('prepare.py','preparation.log',guard));stages.append(stage('transfer.py','transfer.log',guard));save('RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages,io_advice=ADVICE))
  files=list(json.loads(pathlib.Path('INPUT_FREEZE.json').read_text())['files'])+list(json.loads(pathlib.Path('RESIDENT_FREEZE.json').read_text())['files'])+['TIME_SERIES_IDENTITIES.jsonl.gz','INPUT_SHA256SUMS','INPUT_FREEZE.json','inputs.log','RUN_STARTED.json','FIXTURE_WORK.json','tests.log','TEST_STATUS.json','PREPARATION_STARTED.json','PREPARATION_PROGRESS.json','RESIDENT_SHA256SUMS','RESIDENT_FREEZE.json','preparation.log','TRANSFER_STARTED.json','TRANSFER_PROGRESS.json','BASE_BLOCKS.json','TRANSFER_PAIRING_CHECK.json','TRANSFER_RUNTIME.json','TRANSFER_BUDGET.json','BUDGET.json','RUNTIME.json','transfer.log']+['raw/block%02d.jsonl.gz'%i for i in range(24)];assert len(files)==len(set(files));hashes=[]
  for f in files:hashes.append(sha(f)+'  '+f+'\n');guard.check()
  guard.check();success=True
 except BaseException as error:
  save('EXECUTION_FAILURE.json',dict(time=time.time(),error=str(error),traceback=traceback.format_exc(),partial_outputs_preserved=True));raise
 finally:guard.stop.set();t.join()
 if guard.error:raise RuntimeError('Monitor failure found during shutdown: '+guard.error['error'])
 assert success and not pathlib.Path('RESOURCE_STOP.json').exists() and not pathlib.Path('MONITOR_FAILURE.json').exists()
 hashes.append(sha('MEMORY_TELEMETRY.jsonl')+'  MEMORY_TELEMETRY.jsonl\n');pathlib.Path('RESULT_SHA256SUMS').write_text(''.join(hashes));save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',elapsed_seconds=time.time()-start,result_manifest_sha256=sha('RESULT_SHA256SUMS'),monitor_failure_checked=True));print('COMPLETE',flush=True)
if __name__=='__main__':main()
