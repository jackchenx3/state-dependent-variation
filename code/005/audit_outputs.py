"""Independent stored-data audit. No experiment imports or simulation."""
from pathlib import Path
from collections import defaultdict,Counter
import json,gzip,hashlib,math,random
P=Path(__file__).resolve().parent;SRC=P.parent/'mismatch_state_policy_v1';checks=0;max_error=0.;min_score=1.;negative_scores=0;neg=Counter();scopes=defaultdict(list)
def check(ok,msg):
 global checks
 checks+=1
 if not ok:raise AssertionError(msg)
def equal(x,y,msg):
 global max_error
 err=abs(x-y);max_error=max(max_error,err);check(err<2e-12,msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def seed(*p):return int(hashlib.sha256('|'.join(map(str,p)).encode()).hexdigest()[:16],16)
def mean(x):return math.fsum(x)/len(x)
def covariance(x,y):return (math.fsum(a*b for a,b in zip(x,y))-len(x)*mean(x)*mean(y))/(len(x)-1)
def q(x,p):
 a=sorted(x);j=(len(a)-1)*p;i=int(j);return a[i]+(j-i)*(a[min(i+1,len(a)-1)]-a[i])
def cls(ci):return 'positive' if ci[0]>0 else ('negative' if ci[1]<0 else 'unresolved')
def sign(a):return 'unresolved' if abs(a)<=1e-12 else ('positive' if a>0 else 'negative')
def load(f):return json.loads((P/f).read_text())
for manifest in ['SOURCE_SHA256SUMS','RESULT_SHA256SUMS']:
 for line in (P/manifest).read_text().splitlines():h,f=line.split(None,1);check(sha(P/f.strip())==h,'manifest '+f)
cfg=load('config.json');check(cfg['master_seed']==2026092108 and cfg['analysis_seed']==2026092109 and cfg['replicates']==24 and cfg['trial_ids']==[0,1] and cfg['endpoint']==25,'fixed design')
for helper in ['baseline_model.py','v2_model.py','v3_model.py','switch_model.py']:check(sha(P/helper)==sha(SRC/helper),'unchanged helper '+helper)
prov=load('INPUT_PROVENANCE.json')
for f,h in prov['source_files'].items():check(sha(SRC/f)==h,'original '+f)
for f,h in prov['frozen_inputs'].items():check(sha(P/f)==h,'frozen input '+f)
start=load('RUN_STARTED.json');check(start['source_manifest_sha256']==sha(P/'SOURCE_SHA256SUMS'),'run source link');check(start['input_provenance_sha256']==sha(P/'INPUT_PROVENANCE.json'),'run inputs link')
original=[]
with gzip.open(SRC/'checkpoints.jsonl.gz','rt') as cf,gzip.open(SRC/'decisions.jsonl.gz','rt') as df:
 for cl,dl in zip(cf,df):
  cp=json.loads(cl);d=json.loads(dl)
  if cp['task'] in [0,1]:
   r={k:cp[k] for k in ['regime','history','family','task','angle','target']};r.update(populations=cp['populations'],decisions=d['decisions']);original.append(r)
check(len(original)==768,'subset size');roster=load('SUBSET_ROSTER.json');allrecs=[];repcount=0;states=['negative','unresolved','positive']
with gzip.open(P/'INPUT_CHECKPOINTS.jsonl.gz','rt') as cf,gzip.open(P/'EVALUATION_SEEDS.jsonl.gz','rt') as sf,gzip.open(P/'replicates.jsonl.gz','rt') as rf,gzip.open(P/'checkpoint_results.jsonl.gz','rt') as cr:
 for rowid,fixed in enumerate(original):
  cp=json.loads(next(cf));check(cp==fixed,'input subset exact');check(roster[rowid]=={k:cp[k] for k in roster[rowid]},'subset roster');key=[cp[k] for k in ['regime','history','family','task']];tr=[]
  for rep in range(24):
   seeds=json.loads(next(sf));raw=json.loads(next(rf));repcount+=1
   for k in ['regime','history','family','task']:check(seeds[k]==cp[k] and raw[k]==cp[k],'replicate key')
   check(seeds['replicate']==rep and raw['replicate']==rep,'replicate order')
   for name in ['mutation','survival']:
    value=seed(2026092108,'diagnostic-'+name,*(key+[rep]));check(raw[name+'_seed']==seeds[name+'_seed']==value,'independent namespace seed');check(value!=seed(2026092106,name,cp['history'],cp['family'],cp['task']),'not original future seed')
   check(raw['generations']==list(range(6,26)) and raw['cell_order']==['OO','OR','RO','RR'],'raw layout');check(len(raw['performance'])==20,'full trajectory')
   for gen in raw['performance']:
    check(len(gen)==4,'four branches')
    for value in gen:check(math.isfinite(value) and value<=1+1e-12,'valid possibly negative performance');min_score=min(min_score,value);negative_scores+=int(value<0)
   tr.append(raw['performance'])
  for early,pos in [('O',0),('R',2)]:
   r=json.loads(next(cr));check([r[k] for k in ['regime','history','family','task','early']]==key+[early],'checkpoint key');check(r['predictions']==cp['decisions'][early],'frozen predictions');d={g:[v[g-6][pos+1]-v[g-6][pos] for v in tr] for g in [6,25]};x,y=d[6],d[25];delta=[b-a for a,b in zip(x,y)];m={g:mean(d[g]) for g in [6,25]};var={g:covariance(d[g],d[g]) for g in [6,25]};cov=covariance(x,y);vd=covariance(delta,delta);ci_seed=seed(2026092109,'checkpoint-ci',*(key+[early]));check(ci_seed==r['checkpoint_ci_seed'],'conditional seed');rng=random.Random(ci_seed);boots={6:[],25:[]}
   for b in range(2000):
    counts=Counter(rng.randrange(24) for _ in range(24))
    for g in [6,25]:boots[g].append(math.fsum(d[g][i]*n for i,n in counts.items())/24)
   cc={}
   for g in [6,25]:
    check(d[g]==r['replicate_contrasts'][str(g)],'contrast pairing');ci=[q(boots[g],.0125),q(boots[g],.9875)];cc[g]=cls(ci)
    for a,b in zip(ci,r['conditional_ci975'][str(g)]):equal(a,b,'conditional interval')
    check(cc[g]==r['conditional_classification'][str(g)],'conditional classification')
   v={}
   for g in [6,25]:
    for rule,i in [('O',pos),('R',pos+1)]:v['performance_'+rule+'_g'+str(g)]=mean([row[g-6][i] for row in tr])
    v['D'+str(g)]=m[g];v['variance_D'+str(g)]=var[g];v['se_D'+str(g)]=math.sqrt(max(0,var[g])/24)
   v.update(covariance_D6_D25=cov,mean_horizon_change=mean(delta),variance_horizon_change=vd,se_horizon_change=math.sqrt(max(0,vd)/24),H=mean(delta)**2-vd/24)
   for a in states:
    for b in states:v['rank_'+a+'_to_'+b]=int(cc[6]==a and cc[25]==b)
   rev=cc[6]!='unresolved' and cc[25]!='unresolved' and cc[6]!=cc[25];v.update(ranking_reversal=int(rev),ranking_unresolved_either=int('unresolved' in cc.values()),ranking_resolved_same=int(cc[6]==cc[25] and cc[6]!='unresolved'))
   for p in 'MGE':
    a=cp['decisions'][early][p]['predicted_O_minus_R_loss'];sg=sign(a);v[p+'_prediction']=a;v[p+'_analytic_tie']=int(sg=='unresolved');v[p+'_choice_O']=int(cp['decisions'][early][p]['choice']=='O')
    for g in [6,25]:
     v[p+'_B'+str(g)]=(a-m[g])**2-var[g]/24;v[p+'_signed_error_g'+str(g)]=a-m[g];v[p+'_resolved_contradiction_g'+str(g)]=int(sg!='unresolved' and cc[g]!='unresolved' and sg!=cc[g]);v[p+'_resolved_agreement_g'+str(g)]=int(sg==cc[g] and sg!='unresolved');v[p+'_ranking_unresolved_g'+str(g)]=int(sg=='unresolved' or cc[g]=='unresolved')
    v[p+'_X']=-2*((a-m[6])*(m[25]-m[6])+(cov-var[6])/24);equal(v[p+'_B25'],v[p+'_B6']+v['H']+v[p+'_X'],'direct error identity');local=bool(v[p+'_resolved_contradiction_g6']);v[p+'_local_and_reversal']=int(local and rev);v[p+'_local_only']=int(local and not rev);v[p+'_reversal_only']=int(not local and rev);v[p+'_neither_resolved_mechanism']=int(not local and not rev)
   for a,b in [('E','M'),('E','G'),('G','M')]:
    for g in [6,25]:v[a+'_minus_'+b+'_B'+str(g)]=v[a+'_B'+str(g)]-v[b+'_B'+str(g)]
   check(set(v)==set(r['values']),'complete metric set')
   for k,value in v.items():equal(value,r['values'][k],'checkpoint '+k)
   for k in ['H']+[p+'_B'+str(g) for p in 'MGE' for g in [6,25]]:neg[k]+=int(r['values'][k]<0)
   allrecs.append(dict(r,values=v))
   for f in ['ALL',cp['family']]:
    for e in ['BOTH',early]:scopes[cp['regime'],f,e,cp['history']].append(v)
 for f in [cf,sf,rf,cr]:check(next(f,None) is None,'no extra data')
check(repcount==18432 and len(allrecs)==1536,'complete workload');summary=load('summary.json');check(len(summary['groups'])==54 and len(summary['histories'])==1296,'complete summary scopes');idx=load('BOOTSTRAP_INDICES.json');rng=random.Random(2026092109)
for reg in ['structured','isotropic']:check(idx[reg]==[[rng.randrange(24) for _ in range(24)] for _ in range(2000)],'history bootstrap indices')
hist={key:{k:mean([r[k] for r in rows]) for k in rows[0]} for key,rows in scopes.items()}
for r in summary['histories']:
 for k,v in hist[r['regime'],r['family'],r['early'],r['history']].items():equal(v,r['values'][k],'history mean')
max_ci=0.
for g in summary['groups']:
 hh=[hist[g['regime'],g['family'],g['early'],i] for i in range(24)];rr=[r for r in allrecs if r['regime']==g['regime'] and (g['family']=='ALL' or r['family']==g['family']) and (g['early']=='BOTH' or r['early']==g['early'])];check(len(rr)==g['checkpoint_count'],'group size')
 for k,n in g['counts'].items():check(sum(r['values'][k] for r in rr)==n,'full category count')
 counts=[Counter(ids) for ids in idx[g['regime']]]
 for k,v in g['values'].items():
  equal(mean([r[k] for r in hh]),v['mean'],'aggregate mean');boot=[math.fsum(hh[i][k]*n for i,n in co.items())/24 for co in counts];ci=[q(boot,.025),q(boot,.975)]
  for a,b in zip(ci,v['ci95']):max_ci=max(max_ci,abs(a-b));equal(a,b,'history interval')
  check(cls(ci)==v['zero_classification'],'history classification')
b=load('BUDGET.json');check(b['population_generation_updates']==768*24*4*20,'updates budget');check(b['new_offspring']==1474560*32 and b['selection_candidate_scores']==1474560*64,'fitness budget');check(b['training_runs']==b['policy_refits']==b['policy_reselections']==0,'no new policy/training')
lines=(P/'ACCOUNTING.psv').read_text().splitlines();j=dict(zip(lines[0].split('|'),lines[1].split('|')));check(j['State']=='COMPLETED' and j['ExitCode']=='0:0' and j['AllocCPUS']=='1' and j['ReqMem']=='2G','scheduler')
audit=dict(status='PASS',checks=checks,replicates=repcount,checkpoints=len(allrecs),max_numeric_discrepancy=max_error,max_history_interval_discrepancy=max_ci,negative_corrected_checkpoint_estimates=dict(neg),minimum_recorded_performance=min_score,negative_performance_records=negative_scores,method='Independent stored-output reconstruction using raw paired trajectories, alternate raw-moment covariance and bootstrap count weights; no experiment imports or new simulation.',discrepancies=[]);(P/'AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
