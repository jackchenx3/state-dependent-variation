"""Frozen noise corrections, paired conditional CIs and history summaries."""
import math,random
from collections import defaultdict
from baseline_model import seed_for
STATES=('negative','unresolved','positive');POLICIES=('M','G','E');FAMILIES=['0','15','30','45','60','75','90','isotropic']
def mean(x):return sum(x)/len(x)
def cov(x,y):
    a,b=mean(x),mean(y);return sum((v-a)*(w-b) for v,w in zip(x,y))/(len(x)-1)
def quantile(x,q):
    v=sorted(x);z=(len(v)-1)*q;i=int(z);f=z-i;return v[i]*(1-f)+v[min(i+1,len(v)-1)]*f

def classify(ci):return 'positive' if ci[0]>0 else ('negative' if ci[1]<0 else 'unresolved')
def sign(x):return 'unresolved' if abs(x)<=1e-12 else ('positive' if x>0 else 'negative')
def corrected(a,x,y):
    n=len(x);mx,my=mean(x),mean(y);vx,vy,cxy=cov(x,x),cov(y,y),cov(x,y);d=[v-u for u,v in zip(x,y)];h=mean(d)**2-cov(d,d)/n;b6=(a-mx)**2-vx/n;b25=(a-my)**2-vy/n
    return dict(B6=b6,B25=b25,H=h,X=b25-b6-h,X_direct=-2*((a-mx)*(my-mx)+(cxy-vx)/n))

def checkpoint_summary(cp,early,trajectories,cfg):
    pos=0 if early=='O' else 2;n=len(trajectories);assert n==24
    ds={g:[tr[g-6][pos+1]-tr[g-6][pos] for tr in trajectories] for g in (6,25)};x,y=ds[6],ds[25];delta=[b-a for a,b in zip(x,y)];key=[cp[k] for k in ('regime','history','family','task')]+[early];bs=seed_for(cfg['analysis_seed'],'checkpoint-ci',*key);rng=random.Random(bs);boot={6:[],25:[]}
    for _ in range(2000):
        ids=[rng.randrange(n) for _ in range(n)]
        for g in (6,25):boot[g].append(sum(ds[g][i] for i in ids)/n)
    ci={g:[quantile(boot[g],.0125),quantile(boot[g],.9875)] for g in (6,25)};cls={g:classify(ci[g]) for g in (6,25)};v={}
    for g in (6,25):
        for rule,i in [('O',pos),('R',pos+1)]:v['performance_'+rule+'_g'+str(g)]=mean([tr[g-6][i] for tr in trajectories])
        v['D'+str(g)]=mean(ds[g]);v['variance_D'+str(g)]=cov(ds[g],ds[g]);v['se_D'+str(g)]=math.sqrt(v['variance_D'+str(g)]/n)
    v.update(covariance_D6_D25=cov(x,y),mean_horizon_change=mean(delta),variance_horizon_change=cov(delta,delta),se_horizon_change=math.sqrt(cov(delta,delta)/n),H=mean(delta)**2-cov(delta,delta)/n)
    for a in STATES:
        for b in STATES:v['rank_'+a+'_to_'+b]=int(cls[6]==a and cls[25]==b)
    reversal=cls[6]!='unresolved' and cls[25]!='unresolved' and cls[6]!=cls[25];v['ranking_reversal']=int(reversal);v['ranking_unresolved_either']=int('unresolved' in cls.values());v['ranking_resolved_same']=int(cls[6]==cls[25] and cls[6]!='unresolved')
    max_identity=0.
    for p in POLICIES:
        pred=cp['decisions'][early][p]['predicted_O_minus_R_loss'];c=corrected(pred,x,y);max_identity=max(max_identity,abs(c['X']-c['X_direct']));sg=sign(pred);v[p+'_prediction']=pred;v[p+'_analytic_tie']=int(sg=='unresolved');v[p+'_choice_O']=int(cp['decisions'][early][p]['choice']=='O')
        for g in (6,25):
            v[p+'_B'+str(g)]=c['B'+str(g)];v[p+'_signed_error_g'+str(g)]=pred-mean(ds[g]);v[p+'_resolved_contradiction_g'+str(g)]=int(sg!='unresolved' and cls[g]!='unresolved' and sg!=cls[g]);v[p+'_resolved_agreement_g'+str(g)]=int(sg==cls[g] and sg!='unresolved');v[p+'_ranking_unresolved_g'+str(g)]=int(sg=='unresolved' or cls[g]=='unresolved')
        v[p+'_X']=c['X'];local=bool(v[p+'_resolved_contradiction_g6']);v[p+'_local_and_reversal']=int(local and reversal);v[p+'_local_only']=int(local and not reversal);v[p+'_reversal_only']=int(not local and reversal);v[p+'_neither_resolved_mechanism']=int(not local and not reversal)
    for a,b in [('E','M'),('E','G'),('G','M')]:
        for g in (6,25):v[a+'_minus_'+b+'_B'+str(g)]=v[a+'_B'+str(g)]-v[b+'_B'+str(g)]
    assert max_identity<1e-12
    return dict(zip(['regime','history','family','task','early'],key),predictions=cp['decisions'][early],replicate_contrasts={str(g):ds[g] for g in (6,25)},checkpoint_ci_seed=bs,conditional_ci975={str(g):ci[g] for g in (6,25)},conditional_classification={str(g):cls[g] for g in (6,25)},values=v,max_identity_error=max_identity)

def summarize(records,indices):
    lookup=defaultdict(list);histories=[];groups=[]
    for r in records:
        for f in ('ALL',r['family']):
            for e in ('BOTH',r['early']):lookup[r['regime'],f,e,r['history']].append(r['values'])
    for reg in ('structured','isotropic'):
        for f in ['ALL']+FAMILIES:
            for e in ('BOTH','O','R'):
                hh=[]
                for h in range(24):
                    rr=lookup[reg,f,e,h];assert len(rr)==(16 if f=='ALL' else 2)*(2 if e=='BOTH' else 1);v={k:mean([r[k] for r in rr]) for k in rr[0]};hh.append(v);histories.append(dict(regime=reg,family=f,early=e,history=h,values=v))
                vals={}
                for k in hh[0]:
                    boot=[sum(hh[i][k] for i in ids)/24 for ids in indices[reg]];ci=[quantile(boot,.025),quantile(boot,.975)];vals[k]=dict(mean=mean([r[k] for r in hh]),ci95=ci,zero_classification=classify(ci))
                rr=[r for r in records if r['regime']==reg and (f=='ALL' or r['family']==f) and (e=='BOTH' or r['early']==e)];counts={k:sum(r['values'][k] for r in rr) for k in vals if k.startswith('rank') or any(tag in k for tag in ['resolved_','ranking_','local_','reversal_only','neither_resolved','analytic_tie'])};groups.append(dict(regime=reg,family=f,early=e,checkpoint_count=len(rr),counts=counts,values=vals))
    return dict(groups=groups,histories=histories,interval_scope='Pointwise whole-history bootstrap for fixed checkpoint panel, retaining conditional Monte Carlo variability; no simultaneous panel guarantee.')
