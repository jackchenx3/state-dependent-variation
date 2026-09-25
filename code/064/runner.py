"""Single allocation; durable start, bounded resources, preserved failures, no retry."""
import os,sys,threading,traceback
from common import *
from resource_guard055 import Guard,monitor,stage

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID')
 # Exclusive creation precedes every scientific action, including input RNGs.
 with (P/'RUN_STARTED.json').open('x') as f:json.dump(dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=time.time(),python=sys.version),f)
 start=time.time();guard=Guard();thread=threading.Thread(target=monitor,args=(guard,),daemon=True);thread.start();steps=[]
 try:
  verify_manifest('SOURCE_SHA256SUMS');verify_references();assert read('TEST_STATUS.json')['status']=='PASS'
  for script,log in [('test064.py','hpc-tests.log'),('make_inputs.py','inputs.log'),('production.py','production.log'),('analyze064.py','analysis.log'),('audit064.py','audit.log')]:
   steps.append(stage(script,log,guard));assert package_bytes()<=LIMIT,'064 finite delivery budget exceeded'
  save('RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=steps));guard.check()
 except BaseException as error:
  save('EXECUTION_FAILURE.json',dict(error=str(error),traceback=traceback.format_exc(),partial_outputs_preserved=True,automatic_retry=False));raise
 finally:guard.stop.set();thread.join()
 if guard.error:raise RuntimeError('Memory monitor failed: '+str(guard.error))
 assert not (P/'RESOURCE_STOP.json').exists() and not (P/'MONITOR_FAILURE.json').exists()
 size=package_bytes();save('DELIVERY_SIZE_CHECK.json',dict(status='PASS' if size<=LIMIT else 'FAIL',bytes=size,limit_bytes=LIMIT));assert size<=LIMIT
 source={line.split('  ',1)[1] for line in (P/'SOURCE_SHA256SUMS').read_text().splitlines()};source.update(('SOURCE_SHA256SUMS','RESULT_SHA256SUMS','COMPLETION.json'))
 files=[str(f.relative_to(P)) for f in sorted(P.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and str(f.relative_to(P)) not in source and not f.name.startswith('.') and not f.name.startswith('slurm-') and not f.name.startswith('submission') and not f.name.endswith('.tmp')];manifest('RESULT_SHA256SUMS',files)
 save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',job_id=os.environ['SLURM_JOB_ID'],elapsed_seconds=time.time()-start,source_sha256=sha(P/'SOURCE_SHA256SUMS'),result_sha256=sha(P/'RESULT_SHA256SUMS'),scientific_status=read('VALIDATION_CHECK.json')['scientific_status'],audit_status=read('AUDIT_CHECK.json')['status'],new_paths=12288,stored_controls=12288,estimates=380))
if __name__=='__main__':main()
