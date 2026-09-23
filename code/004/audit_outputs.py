"""Independent stored-data audit; no experiment imports or transfer simulation."""
from pathlib import Path
from collections import defaultdict
from itertools import zip_longest
import json,gzip,hashlib,random,math
P=Path(__file__).resolve().parent;checks=0;max_prediction=0.;max_interval=0.
def check(ok,label):
    global checks
    checks+=1
    if not ok:raise AssertionError(label)
def avg(v):return sum(v)/len(v)
def close(x,y):return abs(x-y)<1e-12
def seed(master,*parts):return int(hashlib.sha256('|'.join(map(str,(master,)+parts)).encode()).hexdigest()[:16],16)
def sha(name):return hashlib.sha256((P/name).read_bytes()).hexdigest()
def transpose(a):return [[a[j][i] for j in (0,1)] for i in (0,1)]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in (0,1)) for j in (0,1)] for i in (0,1)]
def mv(a,x):return [sum(a[i][j]*x[j] for j in (0,1)) for i in (0,1)]
def add(a,b):return [[a[i][j]+b[i][j] for j in (0,1)] for i in (0,1)]
ZERO=[[0.,0.],[0.,0.]]
def gaussian(m,t,target,a,beta):
    # Whiten the fitness metric, not the covariance; valid at singular T.
    l00=math.sqrt(a[0][0]);l10=a[1][0]/l00;l11=math.sqrt(a[1][1]-l10*l10);b=[[l00,l10],[0.,l11]]
    s=mm(mm(b,t),transpose(b));u=mv(b,[m[i]-target[i] for i in (0,1)]);d=[[float(i==j)+2*beta*s[i][j] for j in (0,1)] for i in (0,1)];det=d[0][0]*d[1][1]-d[0][1]*d[1][0];inv=[[d[1][1]/det,-d[0][1]/det],[-d[1][0]/det,d[0][0]/det]];ku=mv(inv,u);v=mm(inv,s)
    return -.5*math.log(det)-beta*sum(u[i]*ku[i] for i in (0,1)),sum(x*x for x in ku)+v[0][0]+v[1][1]
def mix(comp):
    b=max(z for z,q in comp);w=[math.exp(z-b) for z,q in comp];return math.fsum(a*q for a,(_,q) in zip(w,comp))/math.fsum(w)
def predictions(pop,target,a,covs):
    mu=[avg([p[i] for p in pop]) for i in (0,1)];s=[[avg([(p[i]-mu[i])*(p[j]-mu[j]) for p in pop]) for j in (0,1)] for i in (0,1)];result={}
    for name in 'MGE':
        result[name]={}
        for rule,c in covs.items():
            comps=([(mu,ZERO),(mu,c)] if name=='M' else ([(mu,s),(mu,add(s,c))] if name=='G' else [(p[:2],t) for p in pop for t in (ZERO,c)]))
            result[name][rule]=mix([gaussian(m,t,target,a,10.) for m,t in comps])
    return result

def sign(x):return 0 if abs(x)<=1e-12 else (1 if x>0 else -1)
def derived(tr,dec):
    v={k:x[-1] for k,x in tr.items()};v['HINDSIGHT']=max(v['ABS_O'],v['ABS_R'])
    for a,b in [('E','M'),('E','G'),('G','M')]+[(p,c) for p in 'MGE' for c in ['CONTINUE','SWITCH','HALF']]:v[a+'_minus_'+b]=v[a]-v[b]
    for g in (6,25):v['observed_loss_O_minus_R_g'+str(g)]=tr['ABS_R'][g-1]-tr['ABS_O'][g-1]
    for p in 'MGE':
        d=dec[p];v[p+'_choose_O']=int(d['choice']=='O');v[p+'_tie']=int(d['tie']);v[p+'_predicted_loss_O_minus_R']=d['predicted_O_minus_R_loss']
        for g in (6,25):
            a=sign(d['predicted_O_minus_R_loss']);b=sign(v['observed_loss_O_minus_R_g'+str(g)])
            v[p+'_sign_accuracy_g'+str(g)]=.5 if a==0 or b==0 else int(a==b)
            v[p+'_decision_error_g'+str(g)]=int(tr[p][g-1]<tr['ABS_R' if d['choice']=='O' else 'ABS_O'][g-1]-1e-12)
    for a,b in [('E','M'),('E','G'),('G','M')]:v[a+'_'+b+'_disagreement']=int(dec[a]['choice']!=dec[b]['choice'])
    return v

def quantile(x,q):
    x=sorted(x);z=(len(x)-1)*q;i=int(z);w=z-i;return x[i]*(1-w)+x[min(i+1,len(x)-1)]*w
cfg=json.loads((P/'config.json').read_text());histories=json.loads((P/'histories.json').read_text());roster=json.loads((P/'roster.json').read_text());pre=json.loads((P/'PRETRAIN_ROSTER.json').read_text());summary=json.loads((P/'summary.json').read_text());idx=json.loads((P/'BOOTSTRAP_INDICES.json').read_text());h=cfg['transfer']['metric_matrix'];groups=defaultdict(list)
for mf in ['SOURCE_SHA256SUMS','RESULT_SHA256SUMS']:
    for line in (P/mf).read_text().splitlines():digest,f=line.split(None,1);check(sha(f.strip())==digest,'manifest '+f)
check(sha('histories.json')==sha('attempts/53279480/histories.json'),'retry training byte identical');check(len(histories)==48 and len(roster)==3072,'cohort sizes');angles={}
for r in histories:check(r['training_seed']==seed(2026092106,'train',r['regime'],r['history']),'training seed');check(0<=r['angle']<math.pi,'valid orientation');angles[r['regime'],r['history']]=r['angle']
for r,p in zip(roster,pre):
    check({k:v for k,v in r.items() if k!='angle'}==p,'pretraining roster');check(r['angle']==angles[r['regime'],r['history']],'fresh orientation')
    for k,namespace in [('target_seed','target'),('mutation_seed','mutation'),('survival_seed','survival')]:check(r[k]==seed(2026092106,namespace,r['history'],r['family'],r['task']),'transfer seed')
    rng=random.Random(r['target_seed']);direction=rng.uniform(0,2*math.pi) if r['family']=='isotropic' else math.radians(float(r['family']));sgn=rng.choice((-1.,1.));check(max(abs(x-y) for x,y in zip(r['target'],[sgn*math.cos(direction),sgn*math.sin(direction)]))<=1e-15,'target generator platform roundoff')
freeze=json.loads((P/'DECISIONS_FROZEN.json').read_text());started=json.loads((P/'CONTINUATIONS_STARTED.json').read_text());check(freeze['freeze_unix']<=started['start_unix'] and freeze['generation_6_and_later_outcomes_started'] is False,'prospective ordering')
for key,name in [('decisions_sha256','decisions.jsonl.gz'),('checkpoints_sha256','checkpoints.jsonl.gz'),('source_manifest_sha256','SOURCE_SHA256SUMS'),('histories_sha256','histories.json'),('roster_sha256','roster.json')]:check(freeze[key]==sha(name),'freeze '+key)
check(started['decisions_freeze_sha256']==sha('DECISIONS_FROZEN.json'),'freeze-linked continuation')
counts=0;min_score=1.;negative_final=0;choice_counts={p:{'O':0,'R':0,'ties':0} for p in 'MGE'}
with gzip.open(P/'checkpoints.jsonl.gz','rt') as cf,gzip.open(P/'decisions.jsonl.gz','rt') as df,gzip.open(P/'branches.jsonl.gz','rt') as bf,gzip.open(P/'policy_outcomes.jsonl.gz','rt') as pf:
    for fixed,cl,dl,bl in zip_longest(roster,cf,df,bf):
        check(all(x is not None for x in (fixed,cl,dl,bl)),'complete rows');cp=json.loads(cl);dec=json.loads(dl);branch=json.loads(bl);counts+=1
        for k,v in fixed.items():check(cp[k]==v and dec[k]==v and branch[k]==v,'roster correspondence')
        check(cp['after_generation']==5 and len(cp['trajectory'])==5 and len(branch['trajectory'])==25,'horizons')
        mut=random.Random(fixed['mutation_seed']);sur=random.Random(fixed['survival_seed'])
        for g in range(5):
            for i in range(32):mut.gauss(0,1);mut.gauss(0,1)
            for i in range(32):sur.random()
        check(json.loads(json.dumps(mut.getstate()))==cp['mutation_random_state'] and json.loads(json.dumps(sur.getstate()))==cp['survival_random_state'],'checkpoint streams')
        target=fixed['target'];den=sum(target[i]*h[i][j]*target[j] for i in (0,1) for j in (0,1));a=[[x/den for x in row] for row in h];covs={}
        for rule in 'OR':
            angle=fixed['angle']+(math.pi/2 if rule=='R' else 0);c=math.cos(angle);s=math.sin(angle);v=.12**2;w=.02**2;covs[rule]=[[v*c*c+w*s*s,(v-w)*c*s],[(v-w)*c*s,v*s*s+w*c*c]]
        for g,row in enumerate(branch['trajectory']):
            for cell,m in row.items():
                if g<5:check(m==cp['trajectory'][g][cell[0]],'early state trajectory')
                residual=[m['centroid'][i]-target[i] for i in (0,1)];cent=sum(residual[i]*a[i][j]*residual[j] for i in (0,1) for j in (0,1));spread=sum(a[i][j]*m['covariance'][j][i] for i in (0,1) for j in (0,1));check(close(cent,m['centroid_loss']) and close(spread,m['dispersion_loss']) and close(cent+spread,1-m['performance']),'loss identity');check(math.isfinite(m['performance']) and m['performance']<=1+1e-12,'performance validity');min_score=min(min_score,m['performance'])
        for early in 'OR':
            row=json.loads(next(pf));check(row['early']==early and all(row[k]==v for k,v in fixed.items()),'policy roster');check(row['decisions']==dec['decisions'][early],'frozen choices preserved');pop=cp['populations'][early];mu=[avg([p[i] for p in pop]) for i in (0,1)];check(mu==cp['trajectory'][-1][early]['centroid'],'checkpoint centroid');check(len(pop)==32 and all(p[2]==fixed['angle']+(math.pi/2 if early=='R' else 0) for p in pop),'checkpoint angles')
            pred=predictions(pop,target,a,covs)
            tr={'ABS_'+r:[g[early+r]['performance'] for g in branch['trajectory']] for r in 'OR'}
            tr['CONTINUE']=list(tr['ABS_'+early]);tr['SWITCH']=list(tr['ABS_'+('R' if early=='O' else 'O')]);tr['HALF']=[(x+y)/2 for x,y in zip(tr['ABS_O'],tr['ABS_R'])]
            for p in 'MGE':
                d=dec['decisions'][early][p]
                for rule in 'OR':err=abs(d['predicted_'+rule+'_loss']-pred[p][rule]);max_prediction=max(max_prediction,err);check(err<1e-12,'independent mixture prediction')
                diff=d['predicted_O_loss']-d['predicted_R_loss'];tie=abs(diff)<=1e-12;choice=early if tie else ('O' if diff<0 else 'R');check(d['choice']==choice and d['tie']==tie and close(diff,d['predicted_O_minus_R_loss']),'fixed decision');check(d['gaussian_component_evaluations']==(128 if p=='E' else 4),'analytic budget');tr[p]=list(tr['ABS_'+choice]);choice_counts[p][choice]+=1;choice_counts[p]['ties']+=int(tie)
            check(tr==row['trajectories'],'prospective branch composition');v=derived(tr,row['decisions'])
            for name,value in v.items():check(close(value,row['values'][name]),'derived value '+name)
            negative_final+=int(min(tr[p][-1] for p in 'MGE')<0)
            for fam in ('ALL',fixed['family']):
                for e in ('BOTH',early):groups[fixed['regime'],fam,e,fixed['history']].append(v)
    check(next(pf,None) is None,'no extra policy outcomes')
check(counts==3072,'paired trial count');hvalues={}
for key,rows in groups.items():hvalues[key]={k:avg([r[k] for r in rows]) for k in rows[0]}
for r in summary['histories']:
    for k,v in hvalues[r['regime'],r['family'],r['early'],r['history']].items():check(close(v,r['values'][k]),'history summary')
rng=random.Random(2026092107)
for reg in ['structured','isotropic']:check(idx[reg]==[[rng.randrange(24) for i in range(24)] for b in range(2000)],'shared bootstrap arrays')
for group in summary['groups']:
    hh=[hvalues[group['regime'],group['family'],group['early'],i] for i in range(24)]
    for k,v in group['values'].items():
        check(close(avg([r[k] for r in hh]),v['mean']),'group mean');boot=[sum(hh[i][k] for i in ids)/24 for ids in idx[group['regime']]];ci=[quantile(boot,.025),quantile(boot,.975)];err=max(abs(x-y) for x,y in zip(ci,v['ci95']));max_interval=max(max_interval,err);check(err<1e-12,'paired interval');check(v['zero_classification']==('positive' if ci[0]>0 else ('negative' if ci[1]<0 else 'unresolved')),'zero classification')
        if 'target_classification' in v:check(v['target_classification']==('above' if ci[0]>.02 else ('below' if ci[1]<.02 else 'unresolved')),'usefulness target')
budget=json.loads((P/'BUDGET.json').read_text());check(budget['per_policy_new_offspring']==800 and budget['per_policy_selection_candidate_scores']==1600 and budget['extra_policy_fitness_probes']==0,'candidate budget');check(budget['total_component_evaluations']=={'M':24576,'G':24576,'E':786432},'total analytic counts')
acc=(P/'ACCOUNTING.psv').read_text().splitlines();parent=dict(zip(acc[0].split('|'),acc[1].split('|')));check(parent['State']=='COMPLETED' and parent['ExitCode']=='0:0' and parent['AllocCPUS']=='1' and parent['ReqMem']=='2G','accounting')
audit=dict(status='PASS',checks=checks,max_prediction_discrepancy=max_prediction,max_interval_discrepancy=max_interval,choice_counts=choice_counts,minimum_branch_performance=min_score,checkpoint_records_with_any_negative_policy_endpoint=negative_final,method='Independent metric-whitened Gaussian calculation, complete branch-composition/seed/freeze audit and paired bootstrap reconstruction; no experiment imports or transfer simulation.',discrepancies=[])
(P/'AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
