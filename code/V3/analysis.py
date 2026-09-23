"""Fixed analysis for two predictors and all directions of grid crossing."""
import math,random
from baseline_model import seed_for
PREDICTORS=('predictor','geometry_predictor')

def mean(x):return math.fsum(x)/len(x)
def signed(x):return 0 if abs(x)<=1e-12 else (1 if x>0 else -1)
def credit(p,d):return .5 if not signed(p) or not signed(d) else float(signed(p)==signed(d))

def crossings(grid,values):
    signs=[signed(x) for x in values];nonzero=[i for i,s in enumerate(signs) if s]
    found=[]
    for a,b in zip(nonzero,nonzero[1:]):
        if signs[a]!=signs[b]:
            found.append(dict(direction='positive_to_negative' if signs[a]>0 else 'negative_to_positive',
                              bracket=[grid[a],grid[b]],tie_points=grid[a+1:b]))
    return dict(crossings=found,tie_points=[g for g,s in zip(grid,signs) if not s],signs=signs)

def crossing_category(p,o):
    if p['tie_points'] or o['tie_points']:return 'ties_present'
    if not p['crossings'] and not o['crossings']:return 'neither_detected'
    if not p['crossings']:return 'observed_only'
    if not o['crossings']:return 'predicted_only'
    return 'same_crossings' if p['crossings']==o['crossings'] else 'different_crossings'

def summarize(cfg,rows,baseline):
    contrasts=[];errors=[];history_signs=[]
    for regime in ('structured','isotropic'):
        for family in list(map(str,cfg['mismatch_degrees']))+['isotropic']:
            rs=[r for r in rows if r['regime']==regime and r['family']==family]
            clusters=[[r for r in rs if r['history']==h] for h in range(cfg['histories_per_regime'])]
            ds=[mean([r['delta'] for r in cluster]) for cluster in clusters]
            ps={p:[mean([r[p] for r in cluster]) for cluster in clusters] for p in PREDICTORS}
            rng=random.Random(seed_for(cfg['seed'],'bootstrap',regime,family))
            bs=sorted(mean([rng.choice(ds) for _ in ds]) for _ in range(cfg['bootstrap_replicates']))
            lo,hi=bs[int(.025*len(bs))],bs[int(.975*len(bs))]
            item=dict(regime=regime,family=family,mean_delta=mean(ds),
                pointwise_95_interval=[lo,hi],classification='benefit' if lo>0 else 'harm' if hi<0 else 'inconclusive',
                history_deltas=ds,history_predictions=ps,
                sign_accuracy={p:mean([credit(a,b) for a,b in zip(ps[p],ds)]) for p in PREDICTORS},
                always_benefit_accuracy=mean([credit(1,d) for d in ds]),
                always_harm_accuracy=mean([credit(-1,d) for d in ds]))
            for arm,index in [('organized',0),('rotated',1)]:
                vals=[r[arm] for r in rs]
                declines=[];negative=[]
                for r in rs:
                    tr=[0.]+[pair[index] for pair in r['trajectory']]
                    declines.append(sum(b<a-1e-12 for a,b in zip(tr,tr[1:])))
                    negative.append(any(x<0 for x in tr))
                item[arm]=dict(mean=mean(vals),ceiling_fraction=mean([float(x>.99) for x in vals]),
                    negative_endpoints=sum(x<0 for x in vals),negative_any=sum(negative),
                    trajectories_with_decline=sum(x>0 for x in declines),declining_transitions=sum(declines),
                    trials=len(rs))
            old=next(c for c in baseline['summary']['contrasts'] if c['regime']==regime and c['family']==family)
            item['v2_reference']=dict(mean_delta=old['mean_delta'],mean_organized=old['mean_organized'],mean_rotated=old['mean_rotated'],
                note='Different fitness metric and fresh transfer noise; values are context, not a same-loss adaptation comparison.')
            for h,d in enumerate(ds):
                record=dict(regime=regime,family=family,history=h,observed_delta=d,observed_sign=signed(d),
                            predictions={p:dict(value=ps[p][h],sign=signed(ps[p][h]),credit=credit(ps[p][h],d)) for p in PREDICTORS})
                history_signs.append(record)
                for p in PREDICTORS:
                    if credit(ps[p][h],d)!=1:
                        errors.append(dict(regime=regime,family=family,history=h,predictor=p,
                            predicted_value=ps[p][h],predicted_sign=signed(ps[p][h]),observed_delta=d,
                            observed_sign=signed(d),credit=credit(ps[p][h],d)))
            contrasts.append(item)
    cross=[];accuracy={}
    for regime in ('structured','isotropic'):
        panel=[c for c in contrasts if c['regime']==regime and c['family']!='isotropic']
        grid=[c['family'] for c in panel]
        for h in range(cfg['histories_per_regime']):
            observed=crossings(grid,[c['history_deltas'][h] for c in panel])
            predicted={p:crossings(grid,[c['history_predictions'][p][h] for c in panel]) for p in PREDICTORS}
            cross.append(dict(regime=regime,history=h,observed=observed,predicted=predicted,
                              agreement={p:crossing_category(predicted[p],observed) for p in PREDICTORS}))
        accuracy[regime]={}
        for p in PREDICTORS:
            scores=[credit(c['history_predictions'][p][h],c['history_deltas'][h]) for c in panel for h in range(cfg['histories_per_regime'])]
            categories=('same_crossings','different_crossings','neither_detected','observed_only','predicted_only','ties_present')
            accuracy[regime][p]=dict(sign_accuracy=mean(scores),weighted_matches=math.fsum(scores),comparisons=len(scores),
                crossing_counts={name:sum(r['agreement'][p]==name for r in cross if r['regime']==regime) for name in categories})
        # Paired history-level accuracy improvement; resample full angle grids.
        changes=[mean([credit(c['history_predictions']['geometry_predictor'][h],c['history_deltas'][h])-
                              credit(c['history_predictions']['predictor'][h],c['history_deltas'][h]) for c in panel])
                 for h in range(cfg['histories_per_regime'])]
        rng=random.Random(seed_for(cfg['seed'],'paired-predictor-accuracy',regime))
        boots=sorted(mean([rng.choice(changes) for _ in changes]) for _ in range(cfg['bootstrap_replicates']))
        accuracy[regime]['geometry_minus_original']=dict(mean=mean(changes),
            exploratory_pointwise_95_interval=[boots[int(.025*len(boots))],boots[int(.975*len(boots))]],
            history_changes=changes)
    return dict(contrasts=contrasts,history_signs=history_signs,errors_and_ties=errors,
                all_crossings=cross,grid_accuracy=accuracy,
                caveat='Conditional reused histories; local weight predictor is not a selected-population theorem. No uniqueness, 45-degree boundary, or multiplicity-adjusted confirmation assumed.')
