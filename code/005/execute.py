import pathlib,os,json,gzip,hashlib,sys,time,subprocess,platform
from model import evaluate
from analysis import checkpoint_summary,summarize
P=pathlib.Path(__file__).resolve().parent;os.chdir(P)
def sha(f):return hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
def save(f,x):pathlib.Path(f).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def main():
 if pathlib.Path('RUN_STARTED.json').exists():raise RuntimeError('Duplicate scientific execution refused')
 for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():h,f=line.split(None,1);assert sha(f.strip())==h
 with open('tests.log','w') as f:r=subprocess.run([sys.executable,'-B','-m','unittest','-v','test_model'],stdout=f,stderr=subprocess.STDOUT)
 save('TEST_STATUS.json',dict(exit_code=r.returncode,tests_log_sha256=sha('tests.log')))
 if r.returncode:raise RuntimeError('Focused tests failed')
 cfg=json.loads(pathlib.Path('config.json').read_text());assert cfg['replicates']==24 and cfg['endpoint']==25 and cfg['master_seed']==2026092108
 start=time.time();save('RUN_STARTED.json',dict(start_unix=start,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),input_provenance_sha256=sha('INPUT_PROVENANCE.json'),job_id=os.environ.get('SLURM_JOB_ID'),python=sys.version,platform=platform.platform()));records=[];minimum=1.;simulation_seconds=0.;conditional_analysis_seconds=0.;repcount=0
 with gzip.open('INPUT_CHECKPOINTS.jsonl.gz','rt') as cf,gzip.open('EVALUATION_SEEDS.jsonl.gz','rt') as sf,gzip.open('replicates.jsonl.gz','wt') as rf,gzip.open('checkpoint_results.jsonl.gz','wt') as out:
  for rownum,line in enumerate(cf):
   cp=json.loads(line);trajectories=[];key={k:cp[k] for k in ('regime','history','family','task')}
   for rep in range(24):
    seeds=json.loads(next(sf));assert all(seeds[k]==v for k,v in key.items()) and seeds['replicate']==rep;then=time.time();tr=evaluate(cfg,cp,seeds);simulation_seconds+=time.time()-then;minimum=min(minimum,min(min(v) for v in tr));rf.write(json.dumps(dict(seeds,generations=list(range(6,26)),cell_order=['OO','OR','RO','RR'],performance=tr),separators=(',',':'),allow_nan=False)+'\n');trajectories.append(tr);repcount+=1
   then=time.time()
   for early in 'OR':
    r=checkpoint_summary(cp,early,trajectories,cfg);out.write(json.dumps(r,separators=(',',':'),allow_nan=False)+'\n');records.append(r)
   conditional_analysis_seconds+=time.time()-then
   if (rownum+1)%32==0:print('Completed pairs',rownum+1,'replicates',repcount,'elapsed',round(time.time()-start,1),flush=True)
  assert next(sf,None) is None
 assert len(records)==1536 and repcount==18432
 save('summary.json',summarize(records,json.loads(pathlib.Path('BOOTSTRAP_INDICES.json').read_text())))
 save('BUDGET.json',dict(training_runs=0,policy_refits=0,policy_reselections=0,pairs=768,checkpoints=1536,evaluation_replicates_per_pair=24,branches_per_replicate=4,generations_per_branch=20,population_generation_updates=1474560,new_offspring=1474560*32,selection_candidate_scores=1474560*64,measurement_loss_calculations=1474560*32,notes='All rollouts are evaluator-only diagnostic costs, unavailable to the frozen operating policies. Same draws couple all four branches within each independent replicate.'))
 save('RUNTIME.json',dict(elapsed_seconds=time.time()-start,simulation_seconds=simulation_seconds,conditional_analysis_seconds=conditional_analysis_seconds,minimum_recorded_performance=minimum,job_id=os.environ.get('SLURM_JOB_ID')))
 files=['tests.log','TEST_STATUS.json','RUN_STARTED.json','replicates.jsonl.gz','checkpoint_results.jsonl.gz','summary.json','BUDGET.json','RUNTIME.json'];pathlib.Path('RESULT_SHA256SUMS').write_text(''.join(sha(f)+'  '+f+'\n' for f in files));save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',finish_unix=time.time(),result_manifest_sha256=sha('RESULT_SHA256SUMS')));print('COMPLETE',flush=True)
if __name__=='__main__':main()
