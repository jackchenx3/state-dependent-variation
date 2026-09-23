"""Cross centroids, COMPLETE centered configurations, and absolute later rules."""
import math,random
from switch_model import advance,draws,measure,set_rule
CELLS=tuple(m+s+r for m in 'OR' for s in 'OR' for r in 'OR')
CONTROLS={'OOO':'OO','OOR':'OR','RRO':'RO','RRR':'RR'}
def centroid(pop):return [sum(p[i] for p in pop)/len(pop) for i in (0,1)]
def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,list) else x

def construct(pops,m,s,angle):
    mu={k:centroid(pops[k]) for k in 'OR'}
    # Keep control coordinates EXACT, with independent containers and fixed angles.
    if m==s:out=set_rule(pops[m],angle)
    else:out=[(mu[m][0]+(p[0]-mu[s][0]),mu[m][1]+(p[1]-mu[s][1]),angle) for p in pops[s]]
    center=centroid(out)
    error=max(abs(center[i]-mu[m][i]) for i in (0,1))
    for a,b in zip(out,pops[s]):
        for i in (0,1):error=max(error,abs((a[i]-center[i])-(b[i]-mu[s][i])))
    if error>1e-12:raise ValueError('assigned centroid/configuration/order mismatch')
    return out,error

def contrasts(y):
    v={}
    for m in 'OR':
        for s in 'OR':v['F_'+m+s]=y[m+s+'O']-y[m+s+'R']
    for s in 'OR':
        for r in 'OR':v['M_'+s+r]=y['O'+s+r]-y['R'+s+r]
    for m in 'OR':
        for r in 'OR':v['S_'+m+r]=y[m+'O'+r]-y[m+'R'+r]
    for s in 'OR':v['IM_'+s]=v['F_O'+s]-v['F_R'+s]
    for m in 'OR':v['IS_'+m]=v['F_'+m+'O']-v['F_'+m+'R']
    v['three_factor']=v['IM_O']-v['IM_R'];v['I_joint']=v['F_OO']-v['F_RR'];v['J_M']=.5*(v['IM_O']+v['IM_R']);v['J_S']=.5*(v['IS_O']+v['IS_R']);v['J_M_minus_J_S']=v['J_M']-v['J_S']
    if abs(v['three_factor']-(v['IS_O']-v['IS_R']))>1e-12 or abs(v['J_M']+v['J_S']-v['I_joint'])>1e-12:raise ValueError('factorial identity mismatch')
    return v

def experiment(cfg,checkpoint):
    c=cfg['transfer'];phi=checkpoint['angle'];target=checkpoint['target'];pops={};max_error=0.
    for cell in CELLS:
        m,s,r=cell;pops[cell],e=construct(checkpoint['populations'],m,s,phi+(math.pi/2 if r=='R' else 0.));max_error=max(max_error,e)
    initial={k:list(v) for k,v in pops.items()}
    traj=[{k:measure(v,target,c['metric_matrix']) for k,v in pops.items()}]
    mut=random.Random();sur=random.Random();mut.setstate(tuples(checkpoint['mutation_random_state']));sur.setstate(tuples(checkpoint['survival_random_state']))
    for g in range(6,26):
        z,u=draws(mut,sur,c['population'])
        for k in CELLS:pops[k]=advance(pops[k],target,c,z,u)
        traj.append({k:measure(v,target,c['metric_matrix']) for k,v in pops.items()})
    ends={k:traj[-1][k]['performance'] for k in CELLS}
    return dict(initial_populations=initial,generations=list(range(5,26)),trajectory=traj,endpoints=ends,contrasts=contrasts(ends),max_transformation_error=max_error)
