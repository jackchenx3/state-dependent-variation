"""Frozen, paired whole-history summaries. No outcome-selected subsets."""
import random,math
from collections import defaultdict
from model import CELLS,contrasts
METRICS=CELLS+tuple(contrasts({k:0. for k in CELLS}))
def mean(xs):return sum(xs)/len(xs)
def quantile(xs,q):
    v=sorted(xs);z=(len(v)-1)*q;i=int(z);f=z-i
    return v[i]*(1-f)+v[min(i+1,len(v)-1)]*f

def summarize(rows,cfg):
    grouped=defaultdict(list)
    for r in rows:grouped[r['regime'],r['family'],r['history']].append(r)
    histories=[]
    for (reg,fam,h),rr in sorted(grouped.items()):
        assert len(rr)==8
        cells={k:mean([r['endpoints'][k] for r in rr]) for k in CELLS}
        histories.append(dict(regime=reg,family=fam,history=h,values=dict(cells,**contrasts(cells))))
    rng=random.Random(cfg['analysis_seed']);families=[]
    for reg in ('structured','isotropic'):
        for fam in [str(x) for x in cfg['transfer']['mismatch_degrees']]+['isotropic']:
            hh=[r for r in histories if r['regime']==reg and r['family']==fam];assert len(hh)==24
            estimates={k:mean([r['values'][k] for r in hh]) for k in METRICS};samples={k:[] for k in METRICS}
            for _ in range(cfg['bootstrap_replicates']):
                ids=[rng.randrange(24) for _ in range(24)]
                for k in METRICS:samples[k].append(mean([hh[i]['values'][k] for i in ids]))
            values={k:dict(mean=estimates[k],ci95=[quantile(samples[k],.025),quantile(samples[k],.975)]) for k in METRICS}
            for v in values.values():v['classification']='positive' if v['ci95'][0]>0 else ('negative' if v['ci95'][1]<0 else 'unresolved')
            rr=[r for r in rows if r['regime']==reg and r['family']==fam]
            trajectories=[]
            for g in range(cfg['endpoint']):
                trajectories.append({cell:{m:mean([r['trajectory'][g][cell][m] for r in rr]) for m in ('performance','centroid_loss','dispersion_loss')} for cell in CELLS})
            families.append(dict(regime=reg,family=fam,values=values,mean_trajectories=trajectories))
    example=[r for r in rows if r['regime']=='structured' and r['history']==0 and r['family']=='75']
    ex=dict(selection='Original illustrative case, not selected anew or representative.',regime='structured',history=0,family='75',endpoints={k:mean([r['endpoints'][k] for r in example]) for k in CELLS},trajectories=[{k:{m:mean([r['trajectory'][g][k][m] for r in example]) for m in ('performance','centroid_loss','dispersion_loss')} for k in CELLS} for g in range(cfg['endpoint'])])
    ex['contrasts']=contrasts(ex['endpoints'])
    return dict(families=families,histories=histories,illustrative_case=ex,analysis_seed=cfg['analysis_seed'],bootstrap_replicates=cfg['bootstrap_replicates'],interval_scope='Pointwise exploratory paired whole-history percentile bootstrap, 24 histories per family; all four cells resampled together. No multiple-testing adjustment.')
