"""Stream exactly four reshaped continuations per stored row; never replay controls."""
import os,struct,itertools,contextlib
from common import *
from operators064 import restore,transform,branches,draws,advance_indices,measure,native_controls
from analysis064 import checked_metrics
from shape064_reference import FAMILIES
PAIRS=('OO','OR','RO','RR')

def main():
 assert os.environ.get('SLURM_JOB_ID') and (P/'INPUT_FREEZE.json').exists()
 verify_manifest('INPUT_SHA256SUMS');assert not (P/'PRODUCTION_STARTED.json').exists()
 save('PRODUCTION_STARTED.json',dict(time=time.time(),job_id=os.environ['SLURM_JOB_ID']))
 with gzip.open(P/'Q.bin.gz','rb') as stream:qbytes=stream.read()
 assert len(qbytes)==1536*7688
 roster=read('roster.json');cfg=read('native_config002.json')['transfer'];h=cfg['metric_matrix']
 assert cfg['population']==32 and cfg['selection_coefficient']==10. and cfg['major_sd']==.12 and cfg['minor_sd']==.02
 (P/'raw').mkdir();(P/'receipts').mkdir();count=0;start=time.time()
 source=iter(zip(rows('checkpoints.jsonl.gz'),rows('outcomes.jsonl.gz')))
 with contextlib.ExitStack() as stack:
  initial=stack.enter_context(BinaryFile(P/'SHAPED_INITIAL.bin.gz','w'))
  moments=stack.enter_context(File(P/'MOMENT_CHECKS.jsonl.gz','w'))
  measurements=stack.enter_context(File(P/'MEASUREMENTS.jsonl.gz','w'))
  endpoints=stack.enter_context(File(P/'PAIR_ENDPOINTS.jsonl.gz','w'))
  for regime in ('structured','isotropic'):
   for history in range(24):
    stem='raw/'+regime+'-h%02d'%history
    with BinaryFile(P/(stem+'.coords.gz'),'w') as coord,BinaryFile(P/(stem+'.indices.gz'),'w') as selected:
     for _ in range(64):
      checkpoint,control=next(source);row=roster[count]
      assert row['regime']==regime and row['history']==history and checkpoint['after_generation']==5
      for k,v in row.items():assert checkpoint[k]==control[k]==v,(count,k)
      qi=history*64+FAMILIES.index(row['family'])*8+row['task'];flat=struct.unpack_from('<961d',qbytes,qi*7688);q=[flat[i*31:(i+1)*31] for i in range(31)]
      shaped={}
      for s in ('O','R'):
       shaped[s],check=transform(checkpoint['populations'][s],q,row['target'],h)
       moments.write(dict(row_index=count,source_state=s,q_index=qi,**check))
      initial.write(struct.pack('<128d',*(x for s in ('O','R') for p in shaped[s] for x in p[:2])))
      pops=branches(shaped,row['angle']);mut,survive=restore(checkpoint);native=native_controls(control);trajectory=[]
      for generation in range(5,26):
       if generation>5:
        normals,uniforms=draws(mut,survive,32);indices=[]
        for c in PAIRS:
         pops[c],ids=advance_indices(pops[c],row['target'],cfg,normals,uniforms);assert len(set(ids))==32;indices.extend(ids)
        selected.write(bytes(indices))
       coord.write(struct.pack('<256d',*(x for c in PAIRS for p in pops[c] for x in p[:2])))
       result=dict(native['trajectory'][generation-5]);result.update({'SHAPE_'+c:measure(pops[c],row['target'],h) for c in PAIRS});trajectory.append(result)
       if generation==5:
        for c in PAIRS:assert abs(result['NATIVE_'+c]['performance']-result['SHAPE_'+c]['performance'])<=1e-12
      y={c:m['performance'] for c,m in trajectory[-1].items()}
      for c,v in native['endpoints'].items():assert y[c]==v
      endpoints.write(dict(row_index=count,**row,cells=y,metrics=checked_metrics(y)))
      measurements.write(dict(row_index=count,first_generation=5,last_generation=25,trajectory=trajectory));count+=1
    save('receipts/'+regime+'-h%02d.json'%history,dict(completed_rows=count,files={stem+s:sha(P/(stem+s)) for s in ('.coords.gz','.indices.gz')},elapsed_seconds=time.time()-start))
    print(regime,history,count,flush=True)
 assert next(source,None) is None and count==3072
 save('PRODUCTION_RUNTIME.json',dict(rows=count,new_paths=count*4,stored_control_paths=count*4,updates=count*80,elapsed_seconds=time.time()-start))
if __name__=='__main__':main()
