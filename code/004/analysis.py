"""Fixed endpoint and diagnostic summaries with regime-shared history draws."""
import math
from collections import defaultdict
POLICIES=('M','G','E');LEVELS=POLICIES+('CONTINUE','SWITCH','HALF','ABS_O','ABS_R','HINDSIGHT')
PAIRS=[('E','M'),('E','G'),('G','M')]+[(p,c) for p in POLICIES for c in ('CONTINUE','SWITCH','HALF')]
def mean(xs):return sum(xs)/len(xs)
def sign(x):return 0 if abs(x)<=1e-12 else (1 if x>0 else -1)
def values(trajectories,decisions):
    v={k:trajectories[k][-1] for k in LEVELS if k!='HINDSIGHT'};v['HINDSIGHT']=max(v['ABS_O'],v['ABS_R'])
    for a,b in PAIRS:v[a+'_minus_'+b]=v[a]-v[b]
    v['observed_loss_O_minus_R_g6']=trajectories['ABS_R'][5]-trajectories['ABS_O'][5];v['observed_loss_O_minus_R_g25']=v['ABS_R']-v['ABS_O']
    for p in POLICIES:
        d=decisions[p];v[p+'_choose_O']=float(d['choice']=='O');v[p+'_tie']=float(d['tie']);v[p+'_predicted_loss_O_minus_R']=d['predicted_O_minus_R_loss']
        for g in (6,25):
            selected=trajectories[p][g-1];other=trajectories['ABS_R' if d['choice']=='O' else 'ABS_O'][g-1]
            v[p+'_decision_error_g'+str(g)]=float(selected<other-1e-12)
            a=sign(d['predicted_O_minus_R_loss']);b=sign(v['observed_loss_O_minus_R_g'+str(g)])
            v[p+'_sign_accuracy_g'+str(g)]=.5 if not a or not b else float(a==b)
    for a,b in [('E','M'),('E','G'),('G','M')]:v[a+'_'+b+'_disagreement']=float(decisions[a]['choice']!=decisions[b]['choice'])
    return v

def quantile(xs,q):
    v=sorted(xs);z=(len(v)-1)*q;i=int(z);f=z-i;return v[i]*(1-f)+v[min(i+1,len(v)-1)]*f

def summarize(records,cfg,indices):
    families=['ALL']+[str(x) for x in cfg['transfer']['mismatch_degrees']]+['isotropic'];histories=[];groups=[]
    lookup=defaultdict(list)
    for r in records:
        for fam in ('ALL',r['family']):
            for early in ('BOTH',r['early']):lookup[r['regime'],fam,early,r['history']].append(r['values'])
    for reg in ('structured','isotropic'):
        for fam in families:
            for early in ('BOTH','O','R'):
                hh=[]
                for h in range(24):
                    rr=lookup[reg,fam,early,h];expected=(64 if fam=='ALL' else 8)*(2 if early=='BOTH' else 1);assert len(rr)==expected
                    vals={k:mean([r[k] for r in rr]) for k in rr[0]};hh.append(vals);histories.append(dict(regime=reg,family=fam,early=early,history=h,values=vals))
                summarized={}
                # Same precomputed regime index arrays for ALL metrics/scopes.
                for k in hh[0]:
                    point=mean([r[k] for r in hh]);boot=[sum(hh[i][k] for i in ids)/24 for ids in indices[reg]];ci=[quantile(boot,.025),quantile(boot,.975)]
                    v=dict(mean=point,ci95=ci,zero_classification='positive' if ci[0]>0 else ('negative' if ci[1]<0 else 'unresolved'))
                    if k in [a+'_minus_'+b for a,b in PAIRS]:v['usefulness_target']=.02;v['target_classification']='above' if ci[0]>.02 else ('below' if ci[1]<.02 else 'unresolved')
                    summarized[k]=v
                groups.append(dict(regime=reg,family=fam,early=early,values=summarized))
    return dict(groups=groups,histories=histories,lead_contrast='E_minus_M',primary_scope='ALL families, BOTH early arms; each regime separately; equal averages within each history',usefulness_target=.02,interval_scope='Paired pointwise exploratory whole-history bootstrap; one fixed index array per regime reused across every table. No multiplicity or separate-interval regime interaction inference.')
