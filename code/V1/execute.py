"""One bounded exploratory run under the user's explicit superseding release."""
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(name, data):
    data=(json.dumps(data,indent=2,allow_nan=False)+'\n').encode()
    with (ROOT/name).open('xb') as stream:
        stream.write(data)

def main():
    job=os.environ.get('SLURM_JOB_ID','')
    if not job.isdigit():
        raise RuntimeError('Slurm compute allocation required')
    (ROOT/'execution_claim').mkdir()
    subprocess.check_call(['sha256sum','-c','SOURCE_SHA256SUMS'],cwd=str(ROOT))
    write_json('runtime.json',dict(job_id=job,hostname=socket.gethostname(),python=sys.version,
               executable=sys.executable,executable_sha256=sha(Path(sys.executable).resolve()),
               platform=platform.platform(),cpus_requested=os.environ.get('SLURM_CPUS_PER_TASK'),
               memory_requested=os.environ.get('SLURM_MEM_PER_NODE'),
               affinity=sorted(os.sched_getaffinity(0)),start_unix=time.time(),
               manifest_sha256=sha(ROOT/'SOURCE_SHA256SUMS')))
    print('RUNNING_CORRECTNESS_TESTS',flush=True)
    with (ROOT/'tests.log').open('xb') as log:
        tested=subprocess.run([sys.executable,'-E','-s','-S','-B','-m','unittest','-v','test_model'],
                              cwd=str(ROOT),stdout=log,stderr=subprocess.STDOUT,timeout=120)
    write_json('test_status.json',dict(exit_code=tested.returncode,log_sha256=sha(ROOT/'tests.log')))
    if tested.returncode:
        raise RuntimeError('correctness tests failed; scientific simulation not started')
    print('TESTS_PASSED_STARTING_FIXED_EXPERIMENT',flush=True)
    from model import assay, summarize, validate_config, validate_roster, predictor
    cfg=json.loads((ROOT/'config.json').read_text())
    validate_config(cfg)
    started=time.time()
    histories,rows=assay(cfg)
    validate_roster(cfg,rows)
    # Additional nonselective provenance checks, no exclusions or reruns.
    angles={(h['regime'],h['history']):h['angle'] for h in histories}
    if len(angles)!=2*cfg['histories_per_regime']:
        raise RuntimeError('invalid history roster')
    for row in rows:
        if row['angle']!=angles[(row['regime'],row['history'])]:
            raise RuntimeError('history mismatch')
        if abs(sum(x*x for x in row['target'])-1)>1e-12:
            raise RuntimeError('target radius mismatch')
        if abs(row['predictor']-predictor(row['angle'],row['target'],cfg['major_sd'],cfg['minor_sd']))>1e-12:
            raise RuntimeError('predictor mismatch')
        for arm in (0,1):
            values=[0.]+[pair[arm] for pair in row['trajectory']]
            if any(b<a-1e-12 for a,b in zip(values,values[1:])):
                raise RuntimeError('selection monotonicity failure')
    summary=summarize(cfg,rows)
    result=dict(config=cfg,histories=histories,rows=rows,summary=summary,
                provenance=dict(job_id=job,hostname=socket.gethostname(),python=sys.version,
                                elapsed_seconds=time.time()-started,
                                source_manifest_sha256=sha(ROOT/'SOURCE_SHA256SUMS'),
                                tests_sha256=sha(ROOT/'tests.log')))
    blob=(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n').encode()
    if len(blob)>cfg['max_result_bytes']:
        raise RuntimeError('fixed application output bound exceeded')
    with (ROOT/'result.partial').open('xb') as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    os.rename(str(ROOT/'result.partial'),str(ROOT/'result.json'))
    write_json('summary.json',summary)
    with (ROOT/'RESULT_SHA256SUMS').open('x') as f:
        for name in ('result.json','summary.json','runtime.json','tests.log','test_status.json'):
            f.write(sha(ROOT/name)+'  '+name+'\n')
    write_json('COMPLETION.json',dict(status='COMPLETE_PENDING_EXTERNAL_ACCOUNTING',job_id=job,
               histories=len(histories),paired_trajectories=len(rows),result_bytes=len(blob),
               result_sha256=sha(ROOT/'result.json'),finish_unix=time.time()))
    print('EXPERIMENT_COMPLETE histories={} paired_trajectories={} elapsed_seconds={:.3f}'.format(
          len(histories),len(rows),time.time()-started),flush=True)

if __name__=='__main__':
    try:
        main()
    except BaseException as error:
        if not (ROOT/'FAILURE.json').exists():
            write_json('FAILURE.json',dict(error_type=type(error).__name__,message=str(error),
                       job_id=os.environ.get('SLURM_JOB_ID'),time_unix=time.time()))
        raise
