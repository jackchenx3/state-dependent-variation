"""Separate stored-data audit, with a precision-matrix Gaussian formula.
No imports of experiment model/analysis and no simulations.
"""
from pathlib import Path
import csv,hashlib,json,math,random
P=Path(__file__).resolve().parent
r=json.loads((P/'result.json').read_text());base=json.loads((P/'baseline_result.json').read_text())
fixed=json.loads((P/'predictions.json').read_text());freeze=json.loads((P/'PREDICTION_FREEZE.json').read_text());cfg=r['config'];s=r['summary']
checks=0;errors=[];max_log_error=0.
def check(ok,msg):
    global checks
    checks+=1
    if not ok:errors.append(msg)
def near(a,b,msg,tol=1e-11):check(abs(a-b)<=tol,msg)
def mean(v):return math.fsum(v)/len(v)
def sign(v):return 0 if abs(v)<=1e-12 else (1 if v>0 else -1)
def credit(p,d):return .5 if not sign(p) or not sign(d) else float(sign(p)==sign(d))
def seed(*parts):return int(hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()[:16],16)
def log_weight(angle,t):
    # Alternative formula using raw-displacement precision Q=C^-1+2 beta A.
    c,z=math.cos(angle),math.sin(angle);v,w=cfg['major_sd']**2,cfg['minor_sd']**2
    c00=v*c*c+w*z*z;c11=v*z*z+w*c*c;c01=(v-w)*c*z;detc=c00*c11-c01*c01
    h=cfg['metric_matrix'];den=h[0][0]*t[0]**2+2*h[0][1]*t[0]*t[1]+h[1][1]*t[1]**2
    a00,a01,a11=h[0][0]/den,h[0][1]/den,h[1][1]/den;beta=cfg['selection_coefficient']
    q00=c11/detc+2*beta*a00;q11=c00/detc+2*beta*a11;q01=-c01/detc+2*beta*a01;detq=q00*q11-q01*q01
    b0=2*beta*(a00*t[0]+a01*t[1]);b1=2*beta*(a01*t[0]+a11*t[1])
    return -beta-.5*math.log(detc*detq)+.5*(q11*b0*b0-2*q01*b0*b1+q00*b1*b1)/detq

def crossing(grid,values):
    signs=[sign(v) for v in values];indices=[i for i,x in enumerate(signs) if x];cs=[]
    for a,b in zip(indices,indices[1:]):
        if signs[a]!=signs[b]:cs.append(dict(direction='positive_to_negative' if signs[a]>0 else 'negative_to_positive',bracket=grid[a:b+1:b-a],tie_points=grid[a+1:b]))
    return dict(crossings=cs,tie_points=[g for g,x in zip(grid,signs) if not x],signs=signs)
def category(p,o):
    if p['tie_points'] or o['tie_points']:return 'ties_present'
    if not p['crossings'] and not o['crossings']:return 'neither_detected'
    if not p['crossings']:return 'observed_only'
    if not o['crossings']:return 'predicted_only'
    return 'same_crossings' if p['crossings']==o['crossings'] else 'different_crossings'
for mf in ('SOURCE_SHA256SUMS','RESULT_SHA256SUMS'):
    for line in (P/mf).read_text().splitlines():
        sha,name=line.split('  ',1);check(hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,'hash '+name)
check(hashlib.sha256((P/'predictions.json').read_bytes()).hexdigest()==freeze['predictions_sha256'],'prediction hash')
check(freeze['freeze_unix']<r['provenance']['scientific_transfer_start_unix'],'recorded freeze before science')
check(r['histories']==base['histories'],'reused histories')
key=lambda x:(x['regime'],x['history'],x['family'],x['task'])
bm={key(x):x for x in base['rows']};fm={key(x):x for x in fixed};rm={key(x):x for x in r['rows']}
check(len(r['rows'])==len(rm)==len(bm)==len(fm)==3072 and set(rm)==set(bm)==set(fm),'complete roster')
for k,row in rm.items():
    check(all(row[f]==bm[k][f] for f in ('angle','target','predictor')),'reused input '+str(k))
    check(all(row[f]==v for f,v in fm[k].items()),'frozen values '+str(k))
    for name,domain in [('mutation_seed','v3-mutation'),('survival_seed','v3-survival')]:check(row[name]==seed(cfg['seed'],domain,row['history'],row['family'],row['task']),'seed '+str(k))
    lw0=log_weight(row['angle'],row['target']);lw1=log_weight(row['angle']+math.pi/2,row['target'])
    for a,b in [(lw0,row['log_weight_organized']),(lw1,row['log_weight_rotated']),(lw0-lw1,row['geometry_predictor'])]:
        max_log_error=max(max_log_error,abs(a-b));near(a,b,'analytic expectation '+str(k))
    near(row['delta'],row['organized']-row['rotated'],'delta '+str(k))
    check(len(row['trajectory'])==25 and all(len(p)==2 and all(math.isfinite(x) and x<=1+1e-12 for x in p) for p in row['trajectory']),'finite scores '+str(k))
    check(row['trajectory'][-1]==[row['organized'],row['rotated']],'endpoint '+str(k))
    check(row['observed_trial_sign']==sign(row['delta']),'observed trial sign')
    for p in ('predictor','geometry_predictor'):
        check(row['predictor_signs'][p]==sign(row[p]),'predictor trial sign')
        expected=None if not sign(row[p]) or not sign(row['delta']) else sign(row[p])!=sign(row['delta'])
        check(row['trial_prediction_errors'][p]==expected,'trial error')
reconstructed={};expected_errors=[]
for contrast in s['contrasts']:
    reg,fam=contrast['regime'],contrast['family'];rows=[x for x in r['rows'] if x['regime']==reg and x['family']==fam]
    ds=[mean([x['delta'] for x in rows if x['history']==h]) for h in range(24)]
    ps={p:[mean([x[p] for x in rows if x['history']==h]) for h in range(24)] for p in ('predictor','geometry_predictor')}
    reconstructed[(reg,fam)]=(ds,ps)
    near(mean(ds),contrast['mean_delta'],'contrast mean')
    rng=random.Random(seed(cfg['seed'],'bootstrap',reg,fam));boots=sorted(mean([rng.choice(ds) for _ in ds]) for _ in range(2000))
    for a,b in zip([boots[50],boots[1950]],contrast['pointwise_95_interval']):near(a,b,'contrast interval')
    check(contrast['classification']==('benefit' if boots[50]>0 else 'harm' if boots[1950]<0 else 'inconclusive'),'classification')
    for p in ps:
        near(mean([credit(a,b) for a,b in zip(ps[p],ds)]),contrast['sign_accuracy'][p],'accuracy')
    for h,d in enumerate(ds):
        for p in ps:
            if credit(ps[p][h],d)!=1:expected_errors.append((reg,fam,h,p))
    for arm,i in [('organized',0),('rotated',1)]:
        near(mean([x[arm] for x in rows]),contrast[arm]['mean'],'arm mean')
        dscores=[[0.]+[q[i] for q in x['trajectory']] for x in rows]
        check(sum(any(v<0 for v in a) for a in dscores)==contrast[arm]['negative_any'],'negative any')
        check(sum(x[arm]<0 for x in rows)==contrast[arm]['negative_endpoints'],'negative endpoints')
        counts=[sum(b<a-1e-12 for a,b in zip(v,v[1:])) for v in dscores]
        check(sum(n>0 for n in counts)==contrast[arm]['trajectories_with_decline'],'declines')
        check(sum(counts)==contrast[arm]['declining_transitions'],'decline count')
check(expected_errors==[(e['regime'],e['family'],e['history'],e['predictor']) for e in s['errors_and_ties']],'complete error list')
for record in s['all_crossings']:
    reg,h=record['regime'],record['history'];grid=list(map(str,cfg['mismatch_degrees']))
    observed=crossing(grid,[reconstructed[(reg,f)][0][h] for f in grid]);check(observed==record['observed'],'all observed crossings')
    for p in ('predictor','geometry_predictor'):
        pred=crossing(grid,[reconstructed[(reg,f)][1][p][h] for f in grid]);check(pred==record['predicted'][p],'all predicted crossings')
        check(category(pred,observed)==record['agreement'][p],'crossing agreement')
for reg in ('structured','isotropic'):
    grid=list(map(str,cfg['mismatch_degrees']));changes=[]
    for h in range(24):
        changes.append(mean([credit(reconstructed[(reg,f)][1]['geometry_predictor'][h],reconstructed[(reg,f)][0][h])-
                             credit(reconstructed[(reg,f)][1]['predictor'][h],reconstructed[(reg,f)][0][h]) for f in grid]))
    a=s['grid_accuracy'][reg]['geometry_minus_original'];near(mean(changes),a['mean'],'paired accuracy difference')
    rng=random.Random(seed(cfg['seed'],'paired-predictor-accuracy',reg));boots=sorted(mean([rng.choice(changes) for _ in changes]) for _ in range(2000))
    for x,y in zip([boots[50],boots[1950]],a['exploratory_pointwise_95_interval']):near(x,y,'paired accuracy interval')
    for p in ('predictor','geometry_predictor'):
        scores=[credit(reconstructed[(reg,f)][1][p][h],reconstructed[(reg,f)][0][h]) for f in grid for h in range(24)]
        near(mean(scores),s['grid_accuracy'][reg][p]['sign_accuracy'],'grid accuracy')
        for name,n in s['grid_accuracy'][reg][p]['crossing_counts'].items():check(n==sum(x['agreement'][p]==name for x in s['all_crossings'] if x['regime']==reg),'crossing counts')
parent=next(x for x in csv.DictReader((P/'ACCOUNTING.psv').read_text().splitlines(),delimiter='|') if x['JobIDRaw']=='53276643')
check(parent['State']=='COMPLETED' and parent['ExitCode']=='0:0' and int(parent['ElapsedRaw'])<=900 and parent['AllocCPUS']=='1','scheduler completion/bounds')
check(json.loads((P/'test_status.json').read_text())['exit_code']==0,'tests passed')
out=dict(status='PASS' if not errors else 'FAIL',checks=checks,errors=errors,max_independent_log_expectation_error=max_log_error,
         method='Read-only stored-output audit; alternate precision-matrix Gaussian formula, independent summary arithmetic, no experiment imports/simulation.',
         verified='Source/result hashes, frozen predictions and recorded ordering, exact historical panel, seeds, both analytic expectations, endpoint/trajectory validity, trial/history signs and failures, contrast CIs, all crossings/missing lists, paired accuracy CIs, decline/negative counts and terminal accounting.')
(P/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if errors:raise SystemExit(1)
