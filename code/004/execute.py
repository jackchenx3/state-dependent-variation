"""All decisions written before any post-checkpoint scientific outcome."""
import pathlib,json,gzip,hashlib,os,time,sys,subprocess,platform
from itertools import zip_longest
from model import checkpoint,decide,continue_branches,compose,budget,seed_roster,bind_frozen_roster
from baseline_model import train,seed_for
from analysis import values,summarize
P=pathlib.Path(__file__).resolve().parent;os.chdir(P)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(name,value):pathlib.Path(name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def main():
    if pathlib.Path('RUN_STARTED.json').exists():raise RuntimeError('Duplicate execution refused')
    for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():
        h,n=line.split(None,1);assert sha(n.strip())==h
    cfg=json.loads(pathlib.Path('config.json').read_text());assert cfg['master_seed']==cfg['transfer']['seed']==2026092106 and cfg['analysis_seed']==2026092107 and cfg['endpoint']==25 and cfg['switch_generation']==5
    with open('tests.log','w') as f:r=subprocess.run([sys.executable,'-B','-m','unittest','-v','test_model'],stdout=f,stderr=subprocess.STDOUT)
    save('TEST_STATUS.json',dict(exit_code=r.returncode,tests_log_sha256=sha('tests.log')))
    if r.returncode:raise RuntimeError('Focused tests failed')
    start=time.time();save('RUN_STARTED.json',dict(start_unix=start,job_id=os.environ.get('SLURM_JOB_ID'),source_manifest_sha256=sha('SOURCE_SHA256SUMS'),python=sys.version,platform=platform.platform(),training_started=False))
    histories=[];training_start=time.time()
    for reg in ('structured','isotropic'):
        for h in range(24):histories.append(dict(regime=reg,history=h,angle=train(cfg['transfer'],reg,h),training_seed=seed_for(cfg['master_seed'],'train',reg,h)))
    save('histories.json',histories);training_seconds=time.time()-training_start
    expected=json.loads(pathlib.Path('PRETRAIN_ROSTER.json').read_text());roster,platform_check=bind_frozen_roster(seed_roster(cfg,histories),expected);save('roster.json',roster);save('TARGET_PLATFORM_CHECK.json',platform_check)
    save('TRAINING_PROVENANCE.json',dict(master_seed=cfg['master_seed'],histories=48,algorithm='Frozen baseline_model.train, elitist training, uniformly chosen final individual',training_seconds=training_seconds,source_sha256=sha('baseline_model.py'),training_generations=120,population=32,training_selection_candidate_scores=48*120*64,new_training_cohort=True))
    decision_seconds=0.;component_counts={'M':0,'G':0,'E':0}
    with gzip.open('checkpoints.jsonl.gz','wt') as cf,gzip.open('decisions.jsonl.gz','wt') as df:
        for i,row in enumerate(roster):
            cp=checkpoint(cfg,row);then=time.perf_counter();decisions=decide(cfg,cp);decision_seconds+=time.perf_counter()-then
            for early in 'OR':
                for p in component_counts:component_counts[p]+=decisions[early][p]['gaussian_component_evaluations']
            cf.write(json.dumps(cp,separators=(',',':'),allow_nan=False)+'\n');df.write(json.dumps(dict(row,decisions=decisions),separators=(',',':'),allow_nan=False)+'\n')
    save('DECISIONS_FROZEN.json',dict(freeze_unix=time.time(),decisions_sha256=sha('decisions.jsonl.gz'),checkpoints_sha256=sha('checkpoints.jsonl.gz'),source_manifest_sha256=sha('SOURCE_SHA256SUMS'),histories_sha256=sha('histories.json'),roster_sha256=sha('roster.json'),checkpoint_count=6144,policy_choices=18432,generation_6_and_later_outcomes_started=False))
    save('BUDGET.json',dict(budget(),decision_runtime_seconds=decision_seconds,total_component_evaluations=component_counts,total_policy_choices=18432,evaluator_pairs=3072,training_seconds=training_seconds))
    save('CONTINUATIONS_STARTED.json',dict(start_unix=time.time(),decisions_freeze_sha256=sha('DECISIONS_FROZEN.json')))
    print('All training/checkpoints/decisions frozen; starting continuations',flush=True)
    records=[];max_identity=0.;min_performance=1.
    with gzip.open('checkpoints.jsonl.gz','rt') as cf,gzip.open('decisions.jsonl.gz','rt') as df,gzip.open('branches.jsonl.gz','wt') as bf,gzip.open('policy_outcomes.jsonl.gz','wt') as pf:
        for i,(cline,dline) in enumerate(zip_longest(cf,df)):
            assert cline is not None and dline is not None;cp=json.loads(cline);fixed=json.loads(dline);assert all(cp[k]==v for k,v in fixed.items() if k!='decisions')
            trajectory=continue_branches(cfg,cp);base=roster[i];bf.write(json.dumps(dict(base,trajectory=trajectory),separators=(',',':'),allow_nan=False)+'\n')
            for g in trajectory:
                for m in g.values():max_identity=max(max_identity,m['identity_error']);min_performance=min(min_performance,m['performance'])
            for early in 'OR':
                dec=fixed['decisions'][early];tr=compose(trajectory,dec,early);v=values(tr,dec)
                record=dict(base,early=early,decisions=dec,trajectories=tr,values=v);pf.write(json.dumps(record,separators=(',',':'),allow_nan=False)+'\n');records.append(dict(base,early=early,values=v))
            if (i+1)%384==0:print('Continuation pairs',i+1,'total elapsed',round(time.time()-start,2),flush=True)
    freeze=json.loads(pathlib.Path('DECISIONS_FROZEN.json').read_text());assert freeze['decisions_sha256']==sha('decisions.jsonl.gz') and freeze['checkpoints_sha256']==sha('checkpoints.jsonl.gz')
    indices=json.loads(pathlib.Path('BOOTSTRAP_INDICES.json').read_text());save('summary.json',summarize(records,cfg,indices))
    save('RUNTIME.json',dict(job_id=os.environ.get('SLURM_JOB_ID'),elapsed_seconds=time.time()-start,pairs=3072,checkpoint_count=6144,policy_choices=18432,max_loss_identity_error=max_identity,minimum_branch_performance=min_performance))
    files=['TARGET_PLATFORM_CHECK.json','histories.json','roster.json','TRAINING_PROVENANCE.json','checkpoints.jsonl.gz','decisions.jsonl.gz','DECISIONS_FROZEN.json','CONTINUATIONS_STARTED.json','BUDGET.json','branches.jsonl.gz','policy_outcomes.jsonl.gz','summary.json','RUNTIME.json','RUN_STARTED.json','tests.log','TEST_STATUS.json']
    pathlib.Path('RESULT_SHA256SUMS').write_text(''.join(sha(f)+'  '+f+'\n' for f in files));save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',finish_unix=time.time(),result_manifest_sha256=sha('RESULT_SHA256SUMS')))
    print('COMPLETE',json.dumps(json.loads(pathlib.Path('RUNTIME.json').read_text())),flush=True)
if __name__=='__main__':main()
