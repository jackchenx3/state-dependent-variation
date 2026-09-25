"""Authenticate inputs, enumerate seeds and map binary layouts, without production draws."""
from common import *
from shape064_reference import seed_for,FAMILIES,BOOTSTRAP_SEED
from analysis064 import METRICS,GROUPS,KEYS,PRIMARY

def main():
 assert not (P/'SOURCE_SHA256SUMS').exists();verify_references();roster=read('roster.json');assert len(roster)==3072
 expected=[(reg,h,f,t) for reg in ('structured','isotropic') for h in range(24) for f in FAMILIES for t in range(8)]
 assert [(q['regime'],q['history'],q['family'],q['task']) for q in roster]==expected
 seeds=[dict(index=h*64+fi*8+t,history=h,family=f,task=t,seed=seed_for(h,f,t)) for h in range(24) for fi,f in enumerate(FAMILIES) for t in range(8)];assert len({q['seed'] for q in seeds})==1536
 for field in ('mutation_seed','survival_seed'):assert len({q[field] for q in roster})==1536
 for i in range(1536):
  a,b=roster[i],roster[i+1536];assert all(a[k]==b[k] for k in ('history','family','task','target','mutation_seed','survival_seed'))
 save('SHAPE_SEEDS.json',seeds);save('METRIC_CATALOG.json',dict(keys=KEYS,metrics=METRICS,groups=GROUPS,primary=PRIMARY,prediction='negative',bootstrap_seed=BOOTSTRAP_SEED,bootstrap_rows=2000,blocks=24,units='normalized performance fractions',interval_scope='approximate pointwise exploratory95%'))
 save('config.json',dict(task_id='ORG-STATE-SHAPE-064',revision=1,task_sha256=sha(P/'ASSIGNMENT.md'),counts=read('COUNTS.json'),source_config='native_config002.json (unchanged original8MiB field applies only to the older package)',endpoint=25,switch_generation=5,orthogonality_tolerance=2e-12,moment_tolerance=1e-12,primary=PRIMARY,working_prediction='negative',resources=dict(cpus=1,memory_GiB=4,minutes=30,partition='norm'),timeout_seconds=1770,delivery_budget_bytes=LIMIT,max_production_allocations=1,new_training=False,native_controls_replayed=False))
 save('DATA_LAYOUT.json',dict(byte_order='little',Q=dict(file='Q.bin.gz',dtype='float64',shape=[1536,31,31],registry='SHAPE_SEEDS.json',uncompressed_matrix_bytes=7688),initial=dict(file='SHAPED_INITIAL.bin.gz',dtype='float64',shape=[3072,2,32,2],source_order=['O','R'],row_mapping='roster.json'),raw=dict(files='raw/{regime}-h{history:02d}.coords.gz',dtype='float64',shape_per_file=[64,21,4,32,2],generations=list(range(5,26)),cell_order=['OO','OR','RO','RR'],local_row='family in fixed order, then task0..7',bytes_per_pair=43008),indices=dict(files='raw/{regime}-h{history:02d}.indices.gz',dtype='uint8',shape_per_file=[64,20,4,32],generations=list(range(6,26)),candidate_order='parents0..31,children32..63',bytes_per_pair=2560),measurements=dict(file='MEASUREMENTS.jsonl.gz',rows=3072,generations=list(range(5,26)),stored_native_values='Original trajectory indices4..24 without recomputation')))
 print('Authenticated3072 rows;1536 seeds enumerated;380 keys; no scientific transformation or RNG')
if __name__=='__main__':main()
