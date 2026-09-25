"""Constructed fixtures and metadata authentication; no production reshaping."""
from pathlib import Path
from fractions import Fraction as F
import datetime,gzip,hashlib,json,math,random,time
from shape064_reference import helmert,positive_qr,sample_q,reshape,metrics,CELLS,FAMILIES,seed_for,BOOTSTRAP_SEED

R=Path(__file__).resolve().parents[1];C=R/'outputs/coordination';S=Path('__EXECUTOR_WORKSPACE__/outputs/mismatch_mechanism_switch_v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=0;maximum=0.;start=time.monotonic()
def check(x):
    global checks
    assert x;checks+=1
def near(a,b,tol=1e-12):
    global maximum
    e=abs(a-b);maximum=max(maximum,e);check(e<=tol)
def moment(p):
    n=len(p);m=[math.fsum(x[k] for x in p)/n for k in (0,1)]
    s=[[math.fsum((x[i]-m[i])*(x[j]-m[j]) for x in p)/n for j in (0,1)] for i in (0,1)]
    return m,s
def loss(p):
    return math.fsum(2*(x-F(2,5))**2+2*(x-F(2,5))*(y-F(4,7))+3*(y-F(4,7))**2 for x,y in p)/len(p)

# Exact rational Householder fixture: initial first two moments fixed, fourth changed.
w=[F(1),F(1),F(1),F(-3)];q=[[F(i==j)-w[i]*w[j]/6 for j in range(4)] for i in range(4)]
d=[[F(-1),F(0)],[F(1),F(0)],[F(0),F(-1)],[F(0),F(1)]]
e=[[sum(q[i][j]*d[j][k] for j in range(4)) for k in (0,1)] for i in range(4)]
for i in range(4):
    check(sum(q[i])==1)
    for j in range(4):check(sum(q[k][i]*q[k][j] for k in range(4))==F(i==j))
for k in (0,1):check(sum(x[k] for x in d)==sum(x[k] for x in e)==0)
for i in (0,1):
    for j in (0,1):check(sum(x[i]*x[j] for x in d)==sum(x[i]*x[j] for x in e))
check(sum((x*x+y*y)**2 for x,y in d)/4==1)
check(sum((x*x+y*y)**2 for x,y in e)/4==F(35,27))
check(loss(d)==loss(e))

for n in (4,32):
    u=helmert(n)
    for j in range(n-1):
        near(math.fsum(row[j] for row in u),0.)
        for k in range(n-1):near(math.fsum(row[j]*row[k] for row in u),float(j==k))
    # These fixed toy seeds are not the production seed namespace.
    q=sample_q(41000+n,n)
    for i in range(n-1):
        for j in range(n-1):near(math.fsum(q[i][k]*q[j][k] for k in range(n-1)),float(i==j),2e-12)
    cases=[[[.3,-.2] for _ in range(n)],[[i/17.,-2*i/17.] for i in range(n)],
           [[((i%5)-2)/7.,((i*i%7)-3)/9.] for i in range(n)]]
    for points in cases:
        before=[row[:] for row in points];changed=reshape(points,q);check(points==before)
        (m,s),(a,b)=moment(points),moment(changed)
        for i in (0,1):
            near(m[i],a[i])
            for j in (0,1):near(s[i][j],b[i][j])
        near(loss(points),loss(changed))
        identity=[[float(i==j) for j in range(n-1)] for i in range(n-1)]
        back=reshape(points,identity)
        for x,y in zip(points,back):
            for i in (0,1):near(x[i],y[i])
    check(sample_q(41000+n,n)==q)

# No forced SO determinant: negating one Gaussian column negates its Q column.
g=[[.2,.7,-.1],[1.1,-.3,.4],[.8,.1,.9]];a=positive_qr(g);b=positive_qr([[-x[0],x[1],x[2]] for x in g])
for i in range(3):
    for j in range(3):near(b[i][j],-a[i][j] if j==0 else a[i][j])
try:positive_qr([[0.,0.],[0.,0.]])
except ValueError:check(True)
else:check(False)
for scale in (-3,0,2):
    y={k:F(scale*(i*i-2*i+1),11) for i,k in enumerate(CELLS)};z=metrics(y)
    check(z['DELTA']==z['G_OO']-z['G_OR']-z['G_RO']+z['G_RR'])
    check(z['DELTA']==z['J_NATIVE']-z['J_SHAPE']);check(len(z)==20)

# Authenticate only needed accepted inputs; no new outcome or scientific replay.
check(sha(S/'DELIVERY_SHA256SUMS')=='c6d376ce583e3abefd07115089f5a8012796b81d8cd81a585b640404c631dba4')
manifests={}
for name in ('SOURCE_SHA256SUMS','RESULT_SHA256SUMS','DELIVERY_SHA256SUMS'):
    manifests[name]={path.strip():digest for digest,path in (line.split(None,1) for line in (S/name).read_text().splitlines())}
needed=['checkpoints.jsonl.gz','outcomes.jsonl.gz','config.json','roster.json','model.py','baseline_model.py','v2_model.py','v3_model.py','analysis.py','summary.json']
inputs={}
for name in needed:
    digest=sha(S/name);check(manifests['DELIVERY_SHA256SUMS'][name]==digest)
    domain='RESULT_SHA256SUMS' if name in ('checkpoints.jsonl.gz','outcomes.jsonl.gz','summary.json') else 'SOURCE_SHA256SUMS'
    check(manifests[domain][name]==digest);inputs[name]={'sha256':digest,'bytes':(S/name).stat().st_size,'original_manifest':domain}
roster=json.loads((S/'roster.json').read_text());check(len(roster)==3072)
expected={(reg,h,f,t) for reg in ('structured','isotropic') for h in range(24) for f in FAMILIES for t in range(8)}
keys=[(r['regime'],r['history'],r['family'],r['task']) for r in roster];check(len(set(keys))==len(keys) and set(keys)==expected)
seeds={seed_for(r['history'],r['family'],r['task']) for r in roster};check(len(seeds)==1536)
check(len({r['mutation_seed'] for r in roster})==1536 and len({r['survival_seed'] for r in roster})==1536)
counts={'historical_blocks':24,'historical_sources':48,'regimes':2,'families_per_regime':8,'trials_per_history_family':8,
        'roster_pairs':3072,'unique_shape_seeds':1536,'shape_gaussian_calls':1536*31*31,
        'new_shaped_states':3072*2,'new_paths':3072*4,'stored_control_paths':3072*4,
        'new_updates':3072*4*20,'new_offspring':3072*4*20*32,'new_candidate_scores':3072*4*20*64,
        'new_selected_state_snapshots':3072*4*21,'new_selected_coordinate_values':3072*4*21*32*2,
        'metrics_per_group':20,'family_groups':16,'all8_regime_groups':2,'regime_difference_groups':1,
        'estimates':20*19,'bootstrap_rows':2000,'bootstrap_indices_per_row':24,'bootstrap_seed':BOOTSTRAP_SEED,
        'reused_normals_calls_if_generated_per_roster_pair':3072*20*64,'reused_uniform_calls_if_generated_per_roster_pair':3072*20*32}
check(counts['new_paths']==12288 and counts['estimates']==380)
record={'status':'PASS','constructed_and_metadata_checks':checks,'max_constructed_float_error':maximum,
        'scientific_checkpoint_states_transformed':0,'new_population_continuations':0,'production_sampler_matrices_generated':0,
        'old_scientific_outcomes_recomputed':0,'checkpoint_and_control_content_read':'Hashes only; roster metadata parsed; no checkpoint traits or control outcomes inspected by this checker.',
        'reference_source_sha256':sha(R/'work/shape064_reference.py'),'checker_source_sha256':sha(Path(__file__)),
        'counts':counts,'elapsed_seconds':time.monotonic()-start,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for name,value in [('ORG-STATE-SHAPE-064-PROSPECTIVE_CHECK.json',record),('ORG-STATE-SHAPE-064-INPUT_BINDINGS.json',{'status':'AUTHENTICATED','source_root':str(S),'original_manifest_hashes':{n:sha(S/n) for n in manifests},'files':inputs,'counts':counts})]:
    with (C/'tasks'/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(record,indent=2))
