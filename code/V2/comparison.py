"""Prospectively specified paired descriptive comparisons; no simulations."""
import math
import random
from baseline_model import seed_for,signed


def compare(cfg,baseline,result):
    a={(c['regime'],c['family']):c for c in baseline['summary']['contrasts']}
    b={(c['regime'],c['family']):c for c in result['summary']['contrasts']}
    contrasts=[]; failures=[]
    for key,new in b.items():
        old=a[key]
        changes=[n-o for n,o in zip(new['history_deltas'],old['history_deltas'])]
        rng=random.Random(seed_for(cfg['seed'],'v2-v1-paired',*key))
        boots=sorted(math.fsum(rng.choice(changes) for _ in changes)/len(changes)
                     for _ in range(cfg['bootstrap_replicates']))
        lo,hi=boots[int(.025*len(boots))],boots[int(.975*len(boots))]
        contrast=dict(regime=key[0],family=key[1],v1=old,v2=new,
                      paired_delta_change=math.fsum(changes)/len(changes),
                      paired_change_pointwise_95_interval=[lo,hi],
                      paired_change_classification='increase' if lo>0 else 'decrease' if hi<0 else 'inconclusive')
        for version,data in [('v1',baseline),('v2',result)]:
            rows=[r for r in data['rows'] if (r['regime'],r['family'])==key]
            diagnostics={}
            for arm,index in [('organized',0),('rotated',1)]:
                declines=[];negative_any=[]
                for row in rows:
                    values=[0.]+[p[index] for p in row['trajectory']]
                    declines.append(sum(y<x-1e-12 for x,y in zip(values,values[1:])))
                    negative_any.append(any(v<0 for v in values))
                diagnostics[arm]=dict(trials=len(rows),negative_endpoints=sum(r[arm]<0 for r in rows),
                    negative_endpoint_fraction=sum(r[arm]<0 for r in rows)/len(rows),
                    trials_with_negative_score=sum(negative_any),trials_with_decline=sum(n>0 for n in declines),
                    declining_transitions=sum(declines),total_transitions=len(rows)*cfg['test_generations'])
            contrast[version+'_diagnostics']=diagnostics
        contrasts.append(contrast)
        for h,(p,d) in enumerate(zip(new['history_predictions'],new['history_deltas'])):
            if signed(p)!=signed(d) or signed(p)==0:
                failures.append(dict(regime=key[0],family=key[1],history=h,predictor=p,v2_delta=d,
                                     v1_delta=old['history_deltas'][h],v2_prediction_sign=signed(p),v2_observed_sign=signed(d)))
    old_brackets={(r['regime'],r['history']):r for r in baseline['summary']['reversal_brackets']}
    bracket_comparison=[dict(regime=r['regime'],history=r['history'],v1=old_brackets[(r['regime'],r['history'])],v2=r)
                        for r in result['summary']['reversal_brackets']]
    accuracy={}
    for regime in ('structured','isotropic'):
        accuracy[regime]={}
        for version,data in [('v1',baseline),('v2',result)]:
            panel=[c for c in data['summary']['contrasts'] if c['regime']==regime and c['family']!='isotropic']
            accuracy[regime][version]=dict(comparisons=len(panel)*cfg['histories_per_regime'],
                weighted_sign_matches=math.fsum(c['sign_accuracy']*cfg['histories_per_regime'] for c in panel),
                sign_accuracy=math.fsum(c['sign_accuracy'] for c in panel)/len(panel),
                always_benefit_accuracy=math.fsum(c['always_benefit_accuracy'] for c in panel)/len(panel),
                always_harm_accuracy=math.fsum(c['always_harm_accuracy'] for c in panel)/len(panel),
                localization=data['summary']['localization_agreement'][regime])
    return dict(contrasts=contrasts,predictor_failures_and_ties=failures,
                bracket_comparison=bracket_comparison,grid_accuracy=accuracy,
                interpretation='Same inherited history inputs; fresh transfer Monte Carlo; exploratory pointwise intervals, no multiplicity correction or new training replication.')
