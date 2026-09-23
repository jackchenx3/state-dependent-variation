"""Fresh training and checkpoint phase, then separately frozen continuations."""
import math,random
from baseline_model import train,seed_for,rotate
from v3_model import covariance,quadratic
from switch_model import advance,draws,measure,set_rule
from policy import decisions
CELLS=('OO','OR','RO','RR');POLICIES=('M','G','E')
def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,list) else x

def seed_roster(cfg,histories):
    rows=[];master=cfg['master_seed']
    for h in histories:
        for family in [str(x) for x in cfg['transfer']['mismatch_degrees']]+['isotropic']:
            for trial in range(8):
                ts=seed_for(master,'target',h['history'],family,trial);rng=random.Random(ts)
                direction=rng.uniform(0,2*math.pi) if family=='isotropic' else math.radians(float(family))
                target=list(rotate((rng.choice((-1.,1.)),0.),direction))
                rows.append(dict(regime=h['regime'],history=h['history'],family=family,task=trial,angle=h['angle'],target=target,target_seed=ts,mutation_seed=seed_for(master,'mutation',h['history'],family,trial),survival_seed=seed_for(master,'survival',h['history'],family,trial)))
    return rows

def checkpoint(cfg,row):
    c=cfg['transfer'];phi=row['angle'];n=c['population'];mut=random.Random(row['mutation_seed']);sur=random.Random(row['survival_seed'])
    pops={k:[(0.,0.,phi+(math.pi/2 if k=='R' else 0.)) for _ in range(n)] for k in 'OR'};trajectory=[]
    for g in range(5):
        z,u=draws(mut,sur,n)
        for k in 'OR':pops[k]=advance(pops[k],row['target'],c,z,u)
        trajectory.append({k:measure(pop,row['target'],c['metric_matrix']) for k,pop in pops.items()})
    return dict(row,populations=pops,trajectory=trajectory,mutation_random_state=mut.getstate(),survival_random_state=sur.getstate(),after_generation=5)

def decide(cfg,cp):
    c=cfg['transfer'];den=quadratic(cp['target'],c['metric_matrix']);a=[[v/den for v in row] for row in c['metric_matrix']]
    covs={k:covariance(cp['angle']+(math.pi/2 if k=='R' else 0.),c['major_sd'],c['minor_sd']) for k in 'OR'}
    # Only current state/model information crosses into the policy function.
    return {early:decisions(cp['populations'][early],cp['target'],a,c['selection_coefficient'],covs,early,cfg['tie_tolerance']) for early in 'OR'}

def continue_branches(cfg,cp):
    c=cfg['transfer'];pops={cell:set_rule(cp['populations'][cell[0]],cp['angle']+(math.pi/2 if cell[1]=='R' else 0.)) for cell in CELLS}
    mut=random.Random();sur=random.Random();mut.setstate(tuples(cp['mutation_random_state']));sur.setstate(tuples(cp['survival_random_state']))
    trajectory=[{cell:g[cell[0]] for cell in CELLS} for g in cp['trajectory']]
    for g in range(6,26):
        z,u=draws(mut,sur,c['population'])
        for k in CELLS:pops[k]=advance(pops[k],cp['target'],c,z,u)
        trajectory.append({k:measure(pop,cp['target'],c['metric_matrix']) for k,pop in pops.items()})
    return trajectory

def compose(trajectory,decision,early):
    branches={r:[g[early+r]['performance'] for g in trajectory] for r in 'OR'}
    values={p:list(branches[decision[p]['choice']]) for p in POLICIES}
    values.update(CONTINUE=list(branches[early]),SWITCH=list(branches['R' if early=='O' else 'O']),HALF=[(a+b)/2 for a,b in zip(branches['O'],branches['R'])],ABS_O=list(branches['O']),ABS_R=list(branches['R']))
    return values

def budget(n=32):
    return dict(per_policy_new_offspring=25*n,per_policy_selection_candidate_scores=25*2*n,per_checkpoint_policy_component_evaluations={'M':4,'G':4,'E':4*n},extra_policy_fitness_probes=0,evaluator_new_offspring_per_pair=(2*5+4*20)*n,evaluator_selection_candidate_scores_per_pair=(2*5+4*20)*2*n,reporting_measurement_loss_calculations_per_pair=(2*5+4*20)*n,notes='Known quadratic-model arithmetic is privileged analytic work, not black-box probes. Extra evaluator branches are not policy observations. HALF is an expectation, not a mixed population.')

def bind_frozen_roster(generated,frozen):
    """Honor literal pretraining targets across platform libm last-bit variation."""
    if len(generated)!=len(frozen):raise ValueError('roster length mismatch')
    rows=[];max_error=0.;different=0
    for row,fixed in zip(generated,frozen):
        for k,v in fixed.items():
            if k=='target':
                err=max(abs(a-b) for a,b in zip(row[k],v));max_error=max(max_error,err);different+=int(row[k]!=v)
                if err>1e-15:raise ValueError('target regeneration exceeds platform roundoff bound')
            elif row[k]!=v:raise ValueError('frozen roster mismatch '+k)
        rows.append(dict(fixed,angle=row['angle']))
    return rows,dict(max_regeneration_difference=max_error,targets_with_last_bit_difference=different,scientific_targets='Exact pretraining frozen literal coordinates; unchanged from original source manifest.')
