"""Single bounded execution with prospective manifest and exact V3 replay audit."""
import pathlib,json,hashlib,time,sys,os,subprocess,gzip,platform,math
from model import experiment,CELLS
from analysis import summarize
P=pathlib.Path(__file__).resolve().parent
os.chdir(P)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(name,value):pathlib.Path(name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def main():
    if pathlib.Path('RUN_STARTED.json').exists():raise RuntimeError('Already started: no automatic duplicate execution')
    for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():
        digest,name=line.split(None,1)
        if sha(name.strip())!=digest:raise RuntimeError('Frozen source mismatch '+name)
    cfg=json.loads(pathlib.Path('config.json').read_text());base=json.loads(pathlib.Path('v3_result.json').read_text());roster=json.loads(pathlib.Path('roster.json').read_text())
    assert sha('v3_result.json')==cfg['v3_result_sha256'];assert cfg['transfer']==base['config'];assert cfg['switch_generation']==5 and cfg['endpoint']==25 and cfg['analysis_seed']==2026092104 and cfg['bootstrap_replicates']==2000
    assert len(roster)==len(base['rows'])==3072
    for a,b in zip(roster,base['rows']):assert all(b[k]==v for k,v in a.items())
    with open('tests.log','w') as out:r=subprocess.run([sys.executable,'-B','-m','unittest','-v','test_model'],stdout=out,stderr=subprocess.STDOUT)
    save('TEST_STATUS.json',dict(exit_code=r.returncode,tests_log_sha256=sha('tests.log')))
    if r.returncode:raise RuntimeError('Focused correctness tests failed')
    start=time.time();save('RUN_STARTED.json',dict(start_unix=start,job_id=os.environ.get('SLURM_JOB_ID'),source_manifest_sha256=sha('SOURCE_SHA256SUMS'),roster_sha256=sha('roster.json'),configuration_sha256=sha('config.json'),python=sys.version,platform=platform.platform(),counterfactual_outcomes_started=False))
    rows=[];max_replay=0.;unequal=0;values=0;max_identity=0.
    with gzip.open('outcomes.jsonl.gz','wt') as out,gzip.open('checkpoints.jsonl.gz','wt') as checkpoints:
        for i,(fixed,old) in enumerate(zip(roster,base['rows'])):
            result,checkpoint=experiment(cfg,fixed)
            for g,traj in enumerate(result['trajectory']):
                for j,cell in enumerate(('OO','RR')):
                    got=traj[cell]['performance'];expected=old['trajectory'][g][j];error=abs(got-expected);max_replay=max(max_replay,error);unequal+=int(got!=expected);values+=1
                    if error>1e-12:raise RuntimeError('V3 replay discrepancy at pair %d generation %d arm %s: %.17g'%(i,g+1,cell,error))
                for cell in CELLS:max_identity=max(max_identity,traj[cell]['identity_error'])
            row=dict(fixed,**result);rows.append(row)
            out.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')
            checkpoints.write(json.dumps(dict(fixed,**checkpoint),separators=(',',':'),allow_nan=False)+'\n')
            if (i+1)%384==0:print('Completed pairs',i+1,'elapsed',round(time.time()-start,2),flush=True)
    save('summary.json',summarize(rows,cfg))
    save('REPLAY_AUDIT.json',dict(status='PASS',checked_performance_values=values,non_bitwise_equal_values=unequal,max_absolute_error=max_replay,max_loss_accounting_error=max_identity,all_3072_pairs_retained=True))
    save('RUNTIME.json',dict(job_id=os.environ.get('SLURM_JOB_ID'),elapsed_seconds=time.time()-start,pairs=len(rows),cells_per_pair=4,checkpoint_populations=6144,recorded_generations=25))
    files=['outcomes.jsonl.gz','checkpoints.jsonl.gz','summary.json','REPLAY_AUDIT.json','RUNTIME.json','RUN_STARTED.json','tests.log','TEST_STATUS.json']
    pathlib.Path('RESULT_SHA256SUMS').write_text(''.join(sha(f)+'  '+f+'\n' for f in files))
    save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',finish_unix=time.time(),result_manifest_sha256=sha('RESULT_SHA256SUMS')))
    print('COMPLETE',json.dumps(json.loads(pathlib.Path('RUNTIME.json').read_text())),flush=True)
if __name__=='__main__':main()
