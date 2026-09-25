"""Fixed20 metrics in19 paired-history groups:380 pointwise estimates."""
import math
from shape064_reference import FAMILIES,CELLS,metrics
METRICS=tuple(metrics({c:0. for c in CELLS}))
REGIMES=('structured','isotropic')
GROUPS=tuple(r+'|'+f for r in REGIMES for f in FAMILIES)+tuple(r+'|ALL8' for r in REGIMES)+('structured_MINUS_isotropic|ALL8',)
KEYS=tuple(g+'|'+m for g in GROUPS for m in METRICS)
PRIMARY='structured|ALL8|DELTA'

def checked_metrics(y):
 out=metrics(y);assert abs(out['DELTA']-(out['G_OO']-out['G_OR']-out['G_RO']+out['G_RR']))<=1e-12
 for shape in ('NATIVE','SHAPE'):assert abs(out['J_'+shape]-(y[shape+'_OO']-y[shape+'_OR']-y[shape+'_RO']+y[shape+'_RR']))<=1e-12
 return out

def aggregate(pair_rows):
 grouped={}
 for q in pair_rows:
  k=q['regime'],q['history'],q['family'];grouped.setdefault(k,[]).append(q['metrics'])
 assert len(grouped)==384 and all(len(v)==8 for v in grouped.values())
 histories={k:{m:sum(q[m] for q in rows)/8 for m in METRICS} for k,rows in grouped.items()}
 groups={r+'|'+f:[histories[r,h,f] for h in range(24)] for r in REGIMES for f in FAMILIES}
 for r in REGIMES:groups[r+'|ALL8']=[{m:sum(histories[r,h,f][m] for f in FAMILIES)/8 for m in METRICS} for h in range(24)]
 groups['structured_MINUS_isotropic|ALL8']=[{m:groups['structured|ALL8'][h][m]-groups['isotropic|ALL8'][h][m] for m in METRICS} for h in range(24)]
 assert tuple(groups)==GROUPS;return histories,groups

def quantile(xs,q):
 v=sorted(xs);z=(len(v)-1)*q;i=int(z);f=z-i;return v[i]*(1-f)+v[min(i+1,len(v)-1)]*f

def estimate(groups,indices):
 assert len(indices)==2000 and all(len(row)==24 and all(type(i)==int and 0<=i<24 for i in row) for row in indices);out={}
 for g in GROUPS:
  for m in METRICS:
   xs=[q[m] for q in groups[g]];samples=[sum(xs[i] for i in row)/24 for row in indices];ci=[quantile(samples,.025),quantile(samples,.975)];out[g+'|'+m]=dict(mean=sum(xs)/24,ci95=ci,classification='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved',history_signs={s:sum((x>0 if s=='positive' else x<0 if s=='negative' else x==0) for x in xs) for s in ('positive','negative','zero')})
 assert tuple(out)==KEYS;return out
