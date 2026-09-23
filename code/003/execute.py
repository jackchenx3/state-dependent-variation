"""Stream the eight-cell fixed design. No new training or seed search."""
import pathlib,json,hashlib,time,sys,os,subprocess,gzip,platform
from collections import defaultdict
from itertools import zip_longest
from model import experiment,CELLS,CONTROLS
from analysis import summarize
P=pathlib.Path(__file__).resolve().parent;os.chdir(P)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(name,value):pathlib.Path(name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def main():
    if pathlib.Path('RUN_STARTED.json').exists():raise RuntimeError('Already started; no automatic duplicate execution')
    for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():
        h,name=line.split(None,1)
        if sha(name.strip())!=h:raise RuntimeError('Frozen source mismatch '+name)
    cfg=json.loads(pathlib.Path('config.json').read_text());original=json.loads(pathlib.Path('input_config.json').read_text());roster=json.loads(pathlib.Path('roster.json').read_text())
    assert cfg['transfer']==original['transfer'] and cfg['switch_generation']==5 and cfg['endpoint']==25 and cfg['analysis_seed']==2026092105 and cfg['bootstrap_replicates']==2000
    for name,h in cfg['inputs'].items():assert sha(name)==h
    assert len(roster)==3072
    with open('tests.log','w') as out:r=subprocess.run([sys.executable,'-B','-m','unittest','-v','test_model'],stdout=out,stderr=subprocess.STDOUT)
    save('TEST_STATUS.json',dict(exit_code=r.returncode,tests_log_sha256=sha('tests.log')))
    if r.returncode:raise RuntimeError('Focused tests failed')
    start=time.time();save('RUN_STARTED.json',dict(start_unix=start,job_id=os.environ.get('SLURM_JOB_ID'),source_manifest_sha256=sha('SOURCE_SHA256SUMS'),roster_sha256=sha('roster.json'),configuration_sha256=sha('config.json'),python=sys.version,platform=platform.platform(),counterfactual_outcomes_started=False))
    rows=[];max_control=0.;unequal=0;values=0;max_identity=0.;max_transform=0.;counts=defaultdict(int);sums={};example=[]
    with gzip.open('input_checkpoints.jsonl.gz','rt') as cpf,gzip.open('input_outcomes.jsonl.gz','rt') as oldf,gzip.open('outcomes.jsonl.gz','wt') as out:
        for i,(fixed,cpline,oldline) in enumerate(zip_longest(roster,cpf,oldf)):
            assert fixed is not None and cpline is not None and oldline is not None
            cp=json.loads(cpline);old=json.loads(oldline)
            assert all(cp[k]==v and old[k]==v for k,v in fixed.items()) and cp['after_generation']==5
            result=experiment(cfg,cp);max_transform=max(max_transform,result['max_transformation_error'])
            for g,traj in zip(result['generations'],result['trajectory']):
                for cell,previous in CONTROLS.items():
                    got=traj[cell]['performance'];expected=old['trajectory'][g-1][previous]['performance'];error=abs(got-expected)
                    if g>=6:values+=1;unequal+=int(got!=expected);max_control=max(max_control,error)
                    if error>1e-12:raise RuntimeError('Control continuation mismatch %d %d %s'%(i,g,cell))
                for cell in CELLS:max_identity=max(max_identity,traj[cell]['identity_error'])
            row=dict(fixed,**result);row['input_checkpoint_row']=i
            out.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')
            key=(fixed['regime'],fixed['family']);counts[key]+=1
            if key not in sums:sums[key]=[{cell:{m:0. for m in ('performance','centroid_loss','dispersion_loss')} for cell in CELLS} for g in range(21)]
            for g,traj in enumerate(result['trajectory']):
                for cell in CELLS:
                    for m in sums[key][g][cell]:sums[key][g][cell][m]+=traj[cell][m]
            rows.append(dict(fixed,endpoints=result['endpoints'],contrasts=result['contrasts']))
            if fixed['regime']=='structured' and fixed['history']==0 and fixed['family']=='75':example.append(row)
            if (i+1)%384==0:print('Completed pairs',i+1,'elapsed',round(time.time()-start,2),flush=True)
    summary=summarize(rows,cfg,sums,counts)
    summary['illustrative_case']=dict(selection='Original illustrative structured history 0 / 75 degrees, not representative.',trial_rows=example)
    save('summary.json',summary)
    save('CONTROL_AUDIT.json',dict(status='PASS',checked_generation_6_to_25_scores=values,non_bitwise_equal_values=unequal,max_absolute_error=max_control,max_loss_accounting_error=max_identity,max_centroid_configuration_error=max_transform,all_3072_pairs_retained=True))
    save('RUNTIME.json',dict(job_id=os.environ.get('SLURM_JOB_ID'),elapsed_seconds=time.time()-start,pairs=len(rows),cells_per_pair=8,recorded_generations=list(range(5,26))))
    files=['outcomes.jsonl.gz','summary.json','CONTROL_AUDIT.json','RUNTIME.json','RUN_STARTED.json','tests.log','TEST_STATUS.json']
    pathlib.Path('RESULT_SHA256SUMS').write_text(''.join(sha(f)+'  '+f+'\n' for f in files))
    save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',finish_unix=time.time(),result_manifest_sha256=sha('RESULT_SHA256SUMS')))
    print('COMPLETE',json.dumps(json.loads(pathlib.Path('RUNTIME.json').read_text())),flush=True)
if __name__=='__main__':main()
