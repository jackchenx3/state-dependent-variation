"""Probabilistic transfer only; no training and no tuning. Python 3.6+."""
import math
import random
from baseline_model import proposal, predictor, seed_for, loss, summarize, validate_config as base_config


def sample_indices(losses, uniforms, coefficient=10.0):
    """Sequential PPS without replacement, preserving original candidate IDs.

    Recenter log weights at EACH draw so surviving underflowed weights recover
    after higher-weight candidates are removed. Common uniforms may couple arms;
    each marginal draw is proportional to exp(-coefficient * squared distance).
    """
    if not losses or len(uniforms)>len(losses) or coefficient<=0 or not math.isfinite(coefficient):
        raise ValueError('invalid sampling dimensions/coefficient')
    if any(not math.isfinite(x) or x<0 for x in losses):
        raise ValueError('invalid squared distances')
    remaining=list(range(len(losses)))
    chosen=[]
    for u in uniforms:
        if not math.isfinite(u) or not 0<=u<1: raise ValueError('uniform outside [0,1)')
        best=min(losses[i] for i in remaining)
        weights=[math.exp(-coefficient*(losses[i]-best)) for i in remaining]
        threshold=u*math.fsum(weights)
        cumulative=0.
        selected=None
        for position,w in enumerate(weights):
            cumulative+=w
            if w>0 and threshold<cumulative:
                selected=position
                break
        if selected is None:
            # Rounding at upper edge only; never choose a zero-weight candidate.
            selected=max(i for i,w in enumerate(weights) if w>0)
        chosen.append(remaining.pop(selected))
    return chosen


def performance(population,target):
    initial=loss((0.,0.),target)
    if initial<=0: raise ValueError('zero initial distance')
    return 1-sum(loss(p[:2],target) for p in population)/(len(population)*initial)


def transfer(cfg,angle,target,mutation_seed,survival_seed):
    mut=random.Random(mutation_seed)
    survive=random.Random(survival_seed)
    n=cfg['population']
    arms=[[(0.,0.,angle+offset) for _ in range(n)] for offset in (0.,math.pi/2)]
    trajectory=[]
    for generation in range(cfg['test_generations']):
        normals=[(mut.gauss(0,1),mut.gauss(0,1)) for _ in range(n)]
        uniforms=[survive.random() for _ in range(n)]
        for j in range(2):
            children=[]
            for (x,y,a),z in zip(arms[j],normals):
                dx,dy=proposal(z,a,cfg['major_sd'],cfg['minor_sd'])
                children.append((x+dx,y+dy,a))
            candidates=arms[j]+children
            indices=sample_indices([loss(p[:2],target) for p in candidates],uniforms,cfg['selection_coefficient'])
            arms[j]=[candidates[i] for i in indices]
        trajectory.append([performance(arm,target) for arm in arms])
    return trajectory


def validate_config(cfg):
    base_config(cfg)
    if cfg['selection_coefficient']!=10.0: raise ValueError('fixed coefficient is 10')


def validate_baseline(cfg,base):
    for key in ('histories_per_regime','population','major_sd','minor_sd',
                'test_generations','tasks_per_family','mismatch_degrees'):
        if cfg[key]!=base['config'][key]: raise ValueError('changed historical/assay input '+key)
    if cfg['seed']==base['config']['seed']: raise ValueError('fresh transfer seed required')
    expected={(reg,h,str(f),t) for reg in ('structured','isotropic')
              for h in range(cfg['histories_per_regime'])
              for f in list(cfg['mismatch_degrees'])+['isotropic']
              for t in range(cfg['tasks_per_family'])}
    keys=[(r['regime'],r['history'],r['family'],r['task']) for r in base['rows']]
    if len(keys)!=len(set(keys)) or set(keys)!=expected: raise ValueError('invalid baseline roster')
    histories={(h['regime'],h['history']):h['angle'] for h in base['histories']}
    if len(histories)!=2*cfg['histories_per_regime']: raise ValueError('invalid historical inputs')
    for r in base['rows']:
        if r['angle']!=histories[(r['regime'],r['history'])]: raise ValueError('historical angle mismatch')


def assay_panel(cfg,baseline):
    """No training call; target/angle copied verbatim; no outcome used as input."""
    rows=[]
    for old in baseline['rows']:
        h,f,t=old['history'],old['family'],old['task']
        ms=seed_for(cfg['seed'],'v2-mutation',h,f,t)
        ss=seed_for(cfg['seed'],'v2-survival',h,f,t)
        traj=transfer(cfg,old['angle'],old['target'],ms,ss)
        a,b=traj[-1]
        rows.append(dict(regime=old['regime'],history=h,family=f,task=t,angle=old['angle'],
                         target=list(old['target']),mutation_seed=ms,survival_seed=ss,
                         predictor=predictor(old['angle'],old['target'],cfg['major_sd'],cfg['minor_sd']),
                         organized=a,rotated=b,delta=a-b,trajectory=traj))
    return baseline['histories'],rows


def validate_rows(cfg,baseline,rows):
    key=lambda r:(r['regime'],r['history'],r['family'],r['task'])
    source={key(r):r for r in baseline['rows']}
    keys=[key(r) for r in rows]
    if len(keys)!=len(set(keys)) or set(keys)!=set(source): raise ValueError('invalid result roster')
    for r in rows:
        old=source[key(r)]
        if r['target']!=old['target'] or r['angle']!=old['angle']: raise ValueError('changed panel')
        if r['predictor']!=old['predictor']: raise ValueError('changed predictor')
        if any(not math.isfinite(r[k]) for k in ('organized','rotated','delta','predictor')):
            raise ValueError('nonfinite endpoint')
        if r['organized']>1+1e-12 or r['rotated']>1+1e-12: raise ValueError('above maximum improvement')
        if abs(r['delta']-(r['organized']-r['rotated']))>1e-12: raise ValueError('delta mismatch')
        traj=r['trajectory']
        if len(traj)!=cfg['test_generations'] or any(len(p)!=2 or any(not math.isfinite(v) or v>1+1e-12 for v in p) for p in traj):
            raise ValueError('invalid trajectory')
        if traj[-1]!=[r['organized'],r['rotated']]: raise ValueError('endpoint mismatch')
        for name,domain in [('mutation_seed','v2-mutation'),('survival_seed','v2-survival')]:
            if r[name]!=seed_for(cfg['seed'],domain,r['history'],r['family'],r['task']):
                raise ValueError('seed mismatch')
    # No lower bound or nondecreasing constraint: declines and negative scores valid.
