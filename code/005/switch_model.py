"""Fixed generation-5 state x later-rule intervention. No training or tuning."""
import math, random
from baseline_model import proposal
from v2_model import sample_indices
from v3_model import normalized_loss,quadratic
CELLS=('OO','OR','RO','RR')

def set_rule(pop,angle):
    # Replace EVERY stored angle, including retained parents; traits/order unchanged.
    return [(x,y,angle) for x,y,_ in pop]

def draws(mut,survive,n):
    return ([(mut.gauss(0,1),mut.gauss(0,1)) for _ in range(n)], [survive.random() for _ in range(n)])

def advance(pop,target,cfg,normals,uniforms):
    children=[]
    for (x,y,a),z in zip(pop,normals):
        dx,dy=proposal(z,a,cfg['major_sd'],cfg['minor_sd']);children.append((x+dx,y+dy,a))
    candidates=pop+children
    losses=[normalized_loss(p[:2],target,cfg['metric_matrix']) for p in candidates]
    ids=sample_indices(losses,uniforms,cfg['selection_coefficient'])
    return [candidates[i] for i in ids]

def measure(pop,target,h):
    n=len(pop);mean=[sum(p[i] for p in pop)/n for i in (0,1)]
    cov=[[sum((p[i]-mean[i])*(p[j]-mean[j]) for p in pop)/n for j in (0,1)] for i in (0,1)]
    loss=sum(normalized_loss(p[:2],target,h) for p in pop)/n
    center=normalized_loss(mean,target,h)
    dispersion=sum(h[i][j]*cov[j][i] for i in (0,1) for j in (0,1))/quadratic(target,h)
    error=abs(loss-center-dispersion)
    if error>1e-12:raise ValueError('loss component identity violated')
    if not all(math.isfinite(x) for x in (loss,center,dispersion)):raise ValueError('nonfinite measurement')
    return dict(performance=1-loss,centroid=mean,covariance=cov,centroid_loss=center,dispersion_loss=dispersion,identity_error=error)

def contrasts(y):
    oo,or_,ro,rr=[y[k] for k in CELLS]
    values=dict(rule_given_O=oo-or_,rule_given_R=ro-rr,state_given_O=oo-ro,state_given_R=or_-rr,interaction=oo-or_-ro+rr,rule=.5*((oo-or_)+(ro-rr)),state=.5*((oo-ro)+(or_-rr)),original=oo-rr)
    if abs(values['rule']+values['state']-values['original'])>1e-12:raise ValueError('factorial identity violated')
    return values

def experiment(cfg,row):
    c=cfg['transfer'];n=c['population'];phi=row['angle'];target=row['target'];switch=cfg['switch_generation']
    mut=random.Random(row['mutation_seed']);survive=random.Random(row['survival_seed'])
    pops={'O':[(0.,0.,phi) for _ in range(n)],'R':[(0.,0.,phi+math.pi/2) for _ in range(n)]}
    early=[];trajectory=[];checkpoint=None
    for g in range(1,cfg['endpoint']+1):
        normals,uniforms=draws(mut,survive,n)
        for k in pops:pops[k]=advance(pops[k],target,c,normals,uniforms)
        metrics={k:measure(p,target,c['metric_matrix']) for k,p in pops.items()}
        if g<=switch:
            early.append(metrics)
            trajectory.append({cell:metrics[cell[0]] for cell in CELLS})
        else:trajectory.append(metrics)
        if g==switch:
            checkpoint=dict(populations=pops,mutation_random_state=mut.getstate(),survival_random_state=survive.getstate(),after_generation=g)
            pops={cell:set_rule(pops[cell[0]],phi+(math.pi/2 if cell[1]=='R' else 0.)) for cell in CELLS}
    endpoints={cell:trajectory[-1][cell]['performance'] for cell in CELLS}
    return dict(trajectory=trajectory,endpoints=endpoints,contrasts=contrasts(endpoints)),checkpoint
