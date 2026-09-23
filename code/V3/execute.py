"""One bounded v3 run; all predictors persisted before scientific outcomes."""
import hashlib,json,os,platform,socket,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    with (ROOT/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def main():
    job=os.environ.get('SLURM_JOB_ID','')
    if not job.isdigit():raise RuntimeError('compute allocation required')
    (ROOT/'execution_claim').mkdir()
    subprocess.check_call(['sha256sum','-c','SOURCE_SHA256SUMS'],cwd=str(ROOT))
    cfg=json.loads((ROOT/'config.json').read_text())
    if sha(ROOT/'baseline_result.json')!=cfg['baseline_result_sha256']:raise RuntimeError('v2 input changed')
    save('runtime.json',dict(job_id=job,hostname=socket.gethostname(),python=sys.version,
        executable_sha256=sha(Path(sys.executable).resolve()),platform=platform.platform(),
        affinity=sorted(os.sched_getaffinity(0)),cpus_requested=os.environ.get('SLURM_CPUS_PER_TASK'),
        memory_requested=os.environ.get('SLURM_MEM_PER_NODE'),start_unix=time.time(),
        source_manifest_sha256=sha(ROOT/'SOURCE_SHA256SUMS')))
    print('CORRECTNESS_TESTS_START',flush=True)
    with (ROOT/'tests.log').open('xb') as f:
        t=subprocess.run([sys.executable,'-E','-s','-S','-B','-m','unittest','-v','test_model'],
                         cwd=str(ROOT),stdout=f,stderr=subprocess.STDOUT,timeout=120)
    save('test_status.json',dict(exit_code=t.returncode,log_sha256=sha(ROOT/'tests.log')))
    if t.returncode:raise RuntimeError('tests failed; scientific transfer not started')
    from model import validate_config,validate_baseline,freeze_predictions,assay_panel,validate_rows
    from analysis import summarize
    baseline=json.loads((ROOT/'baseline_result.json').read_text())
    validate_config(cfg);validate_baseline(cfg,baseline)
    predictions=freeze_predictions(cfg,baseline)
    save('predictions.json',predictions)
    save('PREDICTION_FREEZE.json',dict(predictions_sha256=sha(ROOT/'predictions.json'),pairs=len(predictions),
        freeze_unix=time.time(),source_manifest_sha256=sha(ROOT/'SOURCE_SHA256SUMS'),scientific_transfer_started=False))
    print('TESTS_PASSED_PREDICTIONS_FROZEN_STARTING_V3',flush=True)
    started=time.time();rows=assay_panel(cfg,predictions)
    validate_rows(cfg,baseline,predictions,rows)
    if sha(ROOT/'predictions.json')!=json.loads((ROOT/'PREDICTION_FREEZE.json').read_text())['predictions_sha256']:
        raise RuntimeError('prediction freeze altered')
    summary=summarize(cfg,rows,baseline)
    result=dict(config=cfg,histories=baseline['histories'],rows=rows,summary=summary,
        provenance=dict(job_id=job,hostname=socket.gethostname(),python=sys.version,
            source_manifest_sha256=sha(ROOT/'SOURCE_SHA256SUMS'),baseline_result_sha256=cfg['baseline_result_sha256'],
            predictions_sha256=sha(ROOT/'predictions.json'),scientific_transfer_start_unix=started,
            elapsed_seconds=time.time()-started,tests_sha256=sha(ROOT/'tests.log')))
    blob=(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n').encode()
    if len(blob)>cfg['max_result_bytes']:raise RuntimeError('application result bound exceeded')
    with (ROOT/'result.partial').open('xb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
    os.rename(str(ROOT/'result.partial'),str(ROOT/'result.json'))
    save('summary.json',summary)
    with (ROOT/'RESULT_SHA256SUMS').open('x') as f:
        for name in ('result.json','summary.json','runtime.json','tests.log','test_status.json','predictions.json','PREDICTION_FREEZE.json'):
            f.write(sha(ROOT/name)+'  '+name+'\n')
    save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',job_id=job,histories=48,paired_trajectories=len(rows),
         result_bytes=len(blob),result_sha256=sha(ROOT/'result.json'),finish_unix=time.time()))
    print('COMPLETE histories=48 pairs={} elapsed={:.3f}'.format(len(rows),time.time()-started),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as e:
        if not (ROOT/'FAILURE.json').exists():save('FAILURE.json',dict(error_type=type(e).__name__,message=str(e),job_id=os.environ.get('SLURM_JOB_ID')))
        raise
