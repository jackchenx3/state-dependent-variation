"""V3 normalized anisotropic loss, exact Gaussian local-weight predictor."""
import math
import random
from baseline_model import proposal,predictor,seed_for,signed
from v2_model import sample_indices,validate_baseline,validate_config as validate_v2_config


def quadratic(v,h):
    return h[0][0]*v[0]*v[0]+2*h[0][1]*v[0]*v[1]+h[1][1]*v[1]*v[1]


def normalized_loss(x,target,h):
    d=quadratic(target,h)
    if not d>0 or not math.isfinite(d):raise ValueError('invalid target normalization')
    v=(x[0]-target[0],x[1]-target[1])
    return quadratic(v,h)/d


def mutation_basis(angle,major,minor):
    c,s=math.cos(angle),math.sin(angle)
    return ((major*c,-minor*s),(major*s,minor*c))


def covariance(angle,major,minor):
    b=mutation_basis(angle,major,minor)
    return [[sum(b[i][k]*b[j][k] for k in (0,1)) for j in (0,1)] for i in (0,1)]


def log_expected_weight(angle,target,h,major,minor,beta):
    """For z~N(0,I), offspring delta=Bz at common x=0.

    A=H/(t'Ht); K=I+2 beta B'AB; b=2 beta B'At.
    log E exp[-beta (Bz-t)'A(Bz-t)] =
        -beta t'At - 0.5 log det K + 0.5 b'K^-1 b.
    Cholesky evaluates the symmetric positive-definite K, without C inversion.
    """
    d=quadratic(target,h)
    if d<=0 or not math.isfinite(d):raise ValueError('invalid target normalization')
    a=[[h[i][j]/d for j in (0,1)] for i in (0,1)]
    basis=mutation_basis(angle,major,minor)
    ab=[[sum(a[i][k]*basis[k][j] for k in (0,1)) for j in (0,1)] for i in (0,1)]
    k=[[float(i==j)+2*beta*sum(basis[l][i]*ab[l][j] for l in (0,1)) for j in (0,1)] for i in (0,1)]
    at=[sum(a[i][j]*target[j] for j in (0,1)) for i in (0,1)]
    b=[2*beta*sum(basis[l][i]*at[l] for l in (0,1)) for i in (0,1)]
    l00=math.sqrt(k[0][0]);l10=k[1][0]/l00;l11=math.sqrt(k[1][1]-l10*l10)
    y0=b[0]/l00;y1=(b[1]-l10*y0)/l11
    return -beta*sum(target[i]*at[i] for i in (0,1))-math.log(l00)-math.log(l11)+.5*(y0*y0+y1*y1)


def geometry_prediction(angle,target,cfg):
    args=(target,cfg['metric_matrix'],cfg['major_sd'],cfg['minor_sd'],cfg['selection_coefficient'])
    a=log_expected_weight(angle,*args)
    b=log_expected_weight(angle+math.pi/2,*args)
    return a-b,a,b


def transfer(cfg,angle,target,mutation_seed,survival_seed):
    mut=random.Random(mutation_seed);survive=random.Random(survival_seed)
    n=cfg['population'];h=cfg['metric_matrix']
    arms=[[(0.,0.,angle+offset) for _ in range(n)] for offset in (0.,math.pi/2)]
    trajectory=[]
    for _ in range(cfg['test_generations']):
        normals=[(mut.gauss(0,1),mut.gauss(0,1)) for _ in range(n)]
        uniforms=[survive.random() for _ in range(n)]
        for j in (0,1):
            children=[]
            for (x,y,a),z in zip(arms[j],normals):
                dx,dy=proposal(z,a,cfg['major_sd'],cfg['minor_sd'])
                children.append((x+dx,y+dy,a))
            candidates=arms[j]+children
            losses=[normalized_loss(p[:2],target,h) for p in candidates]
            selected=sample_indices(losses,uniforms,cfg['selection_coefficient'])
            arms[j]=[candidates[i] for i in selected]
        trajectory.append([1-sum(normalized_loss(p[:2],target,h) for p in arm)/n for arm in arms])
    return trajectory


def validate_config(cfg):
    validate_v2_config(cfg)
    expected=[[3.25,3*math.sqrt(3)/4],[3*math.sqrt(3)/4,1.75]]
    if cfg['metric_matrix']!=expected or cfg['metric_angle_degrees']!=30 or cfg['metric_eigenvalues']!=[4,1]:
        raise ValueError('fixed metric changed')


def freeze_predictions(cfg,baseline):
    """Executed for the entire panel before ANY v3 transfer outcomes."""
    rows=[]
    for old in baseline['rows']:
        h,f,t=old['history'],old['family'],old['task']
        g,lw0,lw1=geometry_prediction(old['angle'],old['target'],cfg)
        rows.append(dict(regime=old['regime'],history=h,family=f,task=t,angle=old['angle'],target=list(old['target']),
            mutation_seed=seed_for(cfg['seed'],'v3-mutation',h,f,t),survival_seed=seed_for(cfg['seed'],'v3-survival',h,f,t),
            predictor=old['predictor'],geometry_predictor=g,log_weight_organized=lw0,log_weight_rotated=lw1,
            predictor_signs=dict(predictor=signed(old['predictor']),geometry_predictor=signed(g))))
    return rows


def assay_panel(cfg,predictions):
    rows=[]
    for fixed in predictions:
        row=dict(fixed)
        trajectory=transfer(cfg,row['angle'],row['target'],row['mutation_seed'],row['survival_seed'])
        a,b=trajectory[-1]
        row.update(organized=a,rotated=b,delta=a-b,trajectory=trajectory,observed_trial_sign=signed(a-b),
                   trial_prediction_errors={p:(None if not row['predictor_signs'][p] or not signed(a-b) else row['predictor_signs'][p]!=signed(a-b)) for p in ('predictor','geometry_predictor')})
        rows.append(row)
    return rows


def validate_rows(cfg,baseline,predictions,rows):
    key=lambda r:(r['regime'],r['history'],r['family'],r['task'])
    base={key(r):r for r in baseline['rows']};fixed={key(r):r for r in predictions}
    if len(rows)!=len(base) or len(set(key(r) for r in rows))!=len(rows) or set(key(r) for r in rows)!=set(base):
        raise ValueError('incomplete or duplicate roster')
    for row in rows:
        old=base[key(row)]
        for name,value in fixed[key(row)].items():
            if row[name]!=value:raise ValueError('changed frozen predictor/input')
        if any(row[n]!=old[n] for n in ('target','angle','predictor')):raise ValueError('changed historical panel')
        d=row['organized']-row['rotated']
        if not math.isfinite(d) or abs(d-row['delta'])>1e-12:raise ValueError('invalid delta')
        if len(row['trajectory'])!=cfg['test_generations'] or any(len(p)!=2 or any(not math.isfinite(x) or x>1+1e-12 for x in p) for p in row['trajectory']):
            raise ValueError('invalid normalized performance; negatives allowed')
        if row['trajectory'][-1]!=[row['organized'],row['rotated']]:raise ValueError('endpoint mismatch')
