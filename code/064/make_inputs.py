"""Allocation-only generation of the prospectively fixed Q and bootstrap draws."""
import os,random,struct
from common import *
from shape064_reference import sample_q,BOOTSTRAP_SEED
from operators064 import orthogonality,basis_check

def main():
 assert os.environ.get('SLURM_JOB_ID') and (P/'RUN_STARTED.json').exists()
 assert not (P/'INPUT_GENERATION_STARTED.json').exists(),'Never redraw input matrices'
 save('INPUT_GENERATION_STARTED.json',dict(time=time.time(),job_id=os.environ['SLURM_JOB_ID']))
 registry=read('SHAPE_SEEDS.json');entries=registry if isinstance(registry,list) else registry['rows']
 errors=[]
 with BinaryFile(P/'Q.bin.gz','w') as stream:
  for entry in entries:
   q=sample_q(entry['seed']);errors.append(orthogonality(q));stream.write(struct.pack('<961d',*(x for row in q for x in row)))
 rng=random.Random(BOOTSTRAP_SEED);save('BOOTSTRAP.json',[[rng.randrange(24) for _ in range(24)] for _ in range(2000)])
 save('Q_CHECKS.json',dict(count=len(errors),basis=basis_check(),errors=errors));assert len(errors)==1536
 freeze_inputs(['Q.bin.gz','BOOTSTRAP.json','SHAPE_SEEDS.json','Q_CHECKS.json','checkpoints.jsonl.gz','outcomes.jsonl.gz','roster.json'])
if __name__=='__main__':main()
