"""Post-run arithmetic/evidence audit; independent of model imports, no simulation."""
from pathlib import Path
import json,hashlib,math,random,csv
P=Path(__file__).resolve().parent
v1=json.loads((P/'baseline_result.json').read_text());v2=json.loads((P/'result.json').read_text())
comparison=json.loads((P/'comparison.json').read_text());cfg=v2['config']
errors=[];checks=0

def check(condition,message):
    global checks
    checks+=1
    if not condition:errors.append(message)
def near(a,b,name):check(abs(a-b)<=1e-12,name)
def avg(x):return math.fsum(x)/len(x)
def sign(x):return 0 if abs(x)<=1e-12 else (1 if x>0 else -1)
def seed(*parts):return int(hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()[:16],16)
for manifest in ('SOURCE_SHA256SUMS','RESULT_SHA256SUMS'):
    for line in (P/manifest).read_text().splitlines():
        expected,name=line.split('  ',1)
        check(hashlib.sha256((P/name).read_bytes()).hexdigest()==expected,'hash '+name)
check(v1['histories']==v2['histories'],'historical inputs')
key=lambda r:(r['regime'],r['history'],r['family'],r['task'])
old={key(r):r for r in v1['rows']};new={key(r):r for r in v2['rows']}
check(len(old)==len(new)==len(v2['rows'])==3072 and set(old)==set(new),'roster')
for k,row in new.items():
    previous=old[k]
    check(all(row[f]==previous[f] for f in ('angle','target','predictor')),'inherited/predictor '+str(k))
    for field,domain in [('mutation_seed','v2-mutation'),('survival_seed','v2-survival')]:
        check(row[field]==seed(cfg['seed'],domain,row['history'],row['family'],row['task']),'recorded seed '+str(k))
    near(row['delta'],row['organized']-row['rotated'],'endpoint delta '+str(k))
    check(row['trajectory'][-1]==[row['organized'],row['rotated']],'endpoint '+str(k))
    check(len(row['trajectory'])==25 and all(len(p)==2 and all(math.isfinite(x) and x<=1+1e-12 for x in p) for p in row['trajectory']),'finite upper-bound trajectory '+str(k))
failures=[]
for contrast in comparison['contrasts']:
    reg,fam=contrast['regime'],contrast['family']
    newmeans=[];oldmeans=[]
    for label,data in [('v1',v1),('v2',v2)]:
        rows=[r for r in data['rows'] if r['regime']==reg and r['family']==fam]
        ds=[avg([r['delta'] for r in rows if r['history']==h]) for h in range(24)]
        ps=[avg([r['predictor'] for r in rows if r['history']==h]) for h in range(24)]
        c=contrast[label]
        near(avg(ds),c['mean_delta'],'mean '+label+str((reg,fam)))
        rng=random.Random(seed(data['config']['seed'],'bootstrap',reg,fam))
        boots=sorted(avg([rng.choice(ds) for _ in ds]) for _ in range(2000))
        for a,b in zip([boots[50],boots[1950]],c['exploratory_pointwise_95_interval']):near(a,b,'CI '+label+str((reg,fam)))
        near(avg([float(sign(p)==sign(d)) if sign(p) and sign(d) else .5 for p,d in zip(ps,ds)]),c['sign_accuracy'],'accuracy '+label+str((reg,fam)))
        for arm,index in [('organized',0),('rotated',1)]:
            near(avg([r[arm] for r in rows]),c['mean_'+arm],'arm mean')
            diag=contrast[label+'_diagnostics'][arm]
            declines=[];neg=[]
            for r in rows:
                vals=[0.]+[p[index] for p in r['trajectory']]
                declines.append(sum(y<x-1e-12 for x,y in zip(vals,vals[1:])))
                neg.append(any(x<0 for x in vals))
            check(diag['trials_with_decline']==sum(x>0 for x in declines),'declining trials')
            check(diag['declining_transitions']==sum(declines),'declining steps')
            check(diag['trials_with_negative_score']==sum(neg),'negative any')
            check(diag['negative_endpoints']==sum(r[arm]<0 for r in rows),'negative endpoints')
        if label=='v1':oldmeans=ds
        else:
            newmeans=ds
            for h,(p,d) in enumerate(zip(ps,ds)):
                if sign(p)!=sign(d) or not sign(p):failures.append((reg,fam,h))
    change=[b-a for a,b in zip(oldmeans,newmeans)]
    near(avg(change),contrast['paired_delta_change'],'paired mean')
    rng=random.Random(seed(cfg['seed'],'v2-v1-paired',reg,fam))
    boots=sorted(avg([rng.choice(change) for _ in change]) for _ in range(2000))
    for a,b in zip([boots[50],boots[1950]],contrast['paired_change_pointwise_95_interval']):near(a,b,'paired CI')
check(failures==[(r['regime'],r['family'],r['history']) for r in comparison['predictor_failures_and_ties']],'complete failure list')
account=list(csv.DictReader((P/'ACCOUNTING.psv').read_text().splitlines(),delimiter='|'))
parent=next(r for r in account if r['JobIDRaw']=='53276437')
check(parent['State']=='COMPLETED' and parent['ExitCode']=='0:0','terminal accounting')
check(parent['AllocCPUS']=='1' and int(parent['ElapsedRaw'])<=900,'resource ceiling')
check(json.loads((P/'test_status.json').read_text())['exit_code']==0,'tests passed')
out=dict(status='PASS' if not errors else 'FAIL',checks=checks,errors=errors,
    method='Stored-output audit only: no model imports, training, transfer or new HPC job.',
    verified='Manifest hashes; exact historical panel/predictor; recorded seeds; endpoints/trajectories; all mean contrasts and bootstrap intervals; paired-change intervals; arm means; sign accuracy/failure roster; negative and declining outcomes; terminal accounting.',
    baseline_sha256=hashlib.sha256((P/'baseline_result.json').read_bytes()).hexdigest(),
    result_sha256=hashlib.sha256((P/'result.json').read_bytes()).hexdigest())
(P/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
if errors:raise SystemExit(1)
