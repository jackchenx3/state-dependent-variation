"""Read-only arithmetic audit, no experiment imports or transfer simulation."""
from pathlib import Path
import gzip,json,math,hashlib,random
from collections import defaultdict
P=Path(__file__).resolve().parent
checks=0

def check(ok,message):
    global checks
    checks+=1
    if not ok:raise AssertionError(message)
def close(a,b):return abs(a-b)<=1e-12
def avg(x):return sum(x)/len(x)
def effects(y):
    a,b,c,d=[y[k] for k in ('OO','OR','RO','RR')]
    return dict(rule_given_O=a-b,rule_given_R=c-d,state_given_O=a-c,state_given_R=b-d,interaction=a-b-c+d,rule=(a-b+c-d)/2,state=(a-c+b-d)/2,original=a-d)
def q(x,p):
    x=sorted(x);z=(len(x)-1)*p;i=int(z);w=z-i
    return x[i]*(1-w)+x[min(i+1,len(x)-1)]*w
base=json.loads((P/'v3_result.json').read_text());cfg=json.loads((P/'config.json').read_text());summary=json.loads((P/'summary.json').read_text())
for mf in ('SOURCE_SHA256SUMS','RESULT_SHA256SUMS'):
    for line in (P/mf).read_text().splitlines():
        h,f=line.split(None,1);check(hashlib.sha256((P/f.strip()).read_bytes()).hexdigest()==h,'manifest '+f)
with gzip.open(P/'outcomes.jsonl.gz','rt') as f:rows=[json.loads(line) for line in f]
check(len(rows)==3072,'complete rows');grouped=defaultdict(list);max_identity=0.;unequal=0
for row,old in zip(rows,base['rows']):
    for k in ('regime','history','family','task','angle','target','mutation_seed','survival_seed'):check(row[k]==old[k],'roster '+k)
    check(len(row['trajectory'])==25,'trajectory length')
    grouped[row['regime'],row['family'],row['history']].append(row)
    h=cfg['transfer']['metric_matrix'];tx,ty=row['target'];den=h[0][0]*tx*tx+2*h[0][1]*tx*ty+h[1][1]*ty*ty
    for g,cells in enumerate(row['trajectory']):
        for j,k in enumerate(('OO','RR')):
            v=cells[k]['performance'];unequal+=int(v!=old['trajectory'][g][j]);check(close(v,old['trajectory'][g][j]),'original replay')
        if g<5:check(cells['OO']==cells['OR'] and cells['RO']==cells['RR'],'pre-switch identical')
        for k,m in cells.items():
            x,y=m['centroid'];dx=x-tx;dy=y-ty;cov=m['covariance']
            center=(h[0][0]*dx*dx+2*h[0][1]*dx*dy+h[1][1]*dy*dy)/den
            spread=sum(h[i][j]*cov[j][i] for i in (0,1) for j in (0,1))/den
            check(close(center,m['centroid_loss']) and close(spread,m['dispersion_loss']),'components')
            err=abs(1-m['performance']-center-spread);max_identity=max(max_identity,err);check(err<1e-12,'loss identity')
            check(math.isfinite(m['performance']) and m['performance']<=1+1e-12,'valid performance')
    for k,v in row['endpoints'].items():check(v==row['trajectory'][-1][k]['performance'],'endpoint')
    for k,v in effects(row['endpoints']).items():check(close(v,row['contrasts'][k]),'trial contrast '+k)
    check(close(row['contrasts']['rule']+row['contrasts']['state'],row['contrasts']['original']),'factorial')
with gzip.open(P/'checkpoints.jsonl.gz','rt') as f:check(sum(1 for _ in f)==3072,'complete checkpoint rows')
with gzip.open(P/'checkpoints.jsonl.gz','rt') as f:
    for row,line in zip(rows,f):
        cp=json.loads(line);check(cp['after_generation']==5,'checkpoint time')
        for k in ('regime','history','family','task','mutation_seed','survival_seed'):check(cp[k]==row[k],'checkpoint roster')
        for arm,cell in [('O','OO'),('R','RR')]:
            pop=cp['populations'][arm];angle=row['angle']+(math.pi/2 if arm=='R' else 0)
            check(len(pop)==32 and all(p[2]==angle for p in pop),'checkpoint angles')
            means=[avg([p[i] for p in pop]) for i in (0,1)]
            cov=[[avg([(p[i]-means[i])*(p[j]-means[j]) for p in pop]) for j in (0,1)] for i in (0,1)]
            check(means==row['trajectory'][4][cell]['centroid'] and cov==row['trajectory'][4][cell]['covariance'],'checkpoint moments N')
        mut=random.Random(row['mutation_seed']);sur=random.Random(row['survival_seed'])
        for g in range(5):
            for i in range(32):mut.gauss(0,1);mut.gauss(0,1)
            for i in range(32):sur.random()
        check(json.loads(json.dumps(mut.getstate()))==cp['mutation_random_state'],'mutation checkpoint stream')
        check(json.loads(json.dumps(sur.getstate()))==cp['survival_random_state'],'survival checkpoint stream')
history_values={}
for key,rr in grouped.items():
    check(len(rr)==8,'eight trials');cells={k:avg([r['endpoints'][k] for r in rr]) for k in ('OO','OR','RO','RR')};history_values[key]=dict(cells,**effects(cells))
for r in summary['histories']:
    y=history_values[r['regime'],r['family'],r['history']]
    for k,v in y.items():check(close(v,r['values'][k]),'history mean')
rng=random.Random(2026092104)
for s in summary['families']:
    hh=[history_values[s['regime'],s['family'],i] for i in range(24)];samples={k:[] for k in hh[0]}
    for b in range(2000):
        ids=[rng.randrange(24) for _ in range(24)]
        for k in samples:samples[k].append(avg([hh[i][k] for i in ids]))
    for k,v in s['values'].items():
        check(close(v['mean'],avg([r[k] for r in hh])),'family mean')
        check(close(v['ci95'][0],q(samples[k],.025)) and close(v['ci95'][1],q(samples[k],.975)),'bootstrap interval')
        expected='positive' if v['ci95'][0]>0 else ('negative' if v['ci95'][1]<0 else 'unresolved');check(v['classification']==expected,'classification')
    rr=[r for r in rows if r['regime']==s['regime'] and r['family']==s['family']]
    for g in range(25):
        for cell in ('OO','OR','RO','RR'):
            for m in ('performance','centroid_loss','dispersion_loss'):check(close(s['mean_trajectories'][g][cell][m],avg([r['trajectory'][g][cell][m] for r in rr])),'family component trajectory')
accounting=(P/'ACCOUNTING.psv').read_text().splitlines()
parent=dict(zip(accounting[0].split('|'),accounting[1].split('|')))
check(parent['State']=='COMPLETED' and parent['ExitCode']=='0:0' and parent['AllocCPUS']=='1' and parent['ReqMem']=='2G','scheduler resources and completion')
start=json.loads((P/'RUN_STARTED.json').read_text());end=json.loads((P/'COMPLETION.json').read_text())
check(start['source_manifest_sha256']==hashlib.sha256((P/'SOURCE_SHA256SUMS').read_bytes()).hexdigest(),'frozen source provenance')
check(start['counterfactual_outcomes_started'] is False and start['start_unix']<end['finish_unix'],'recorded freeze ordering')
out=dict(status='PASS',checks=checks,max_loss_identity_error=max_identity,original_non_bitwise_equal_values=unequal,method='Stored-output arithmetic and bootstrap audit; no experiment imports, no transfer simulation. Checkpoint RNG states reconstructed from seeds only.',discrepancies=[])
(P/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
