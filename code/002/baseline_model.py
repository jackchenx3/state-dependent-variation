"""Abstract 2-D inherited-orientation model. No biological sequence inputs.

Library has no import-time simulation. Run only through the reviewed HPC gate.
Python >=3.6, standard library only.
"""
import math
import random


def seed_for(master, *parts):
    import hashlib
    return int(hashlib.sha256(('|'.join(map(str, (master,) + parts))).encode()).hexdigest()[:16], 16)


def rotate(v, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (c*v[0]-s*v[1], s*v[0]+c*v[1])


def proposal(z, angle, major, minor):
    return rotate((major*z[0], minor*z[1]), angle)


def loss(x, target):
    return sum((a-b)**2 for a, b in zip(x, target))


def select(population, target, n):
    # Stable tie handling is identical between paired arms.
    return sorted(population, key=lambda p: loss(p[:2], target))[:n]


def train(cfg, regime, history):
    """Training has no test targets, test seeds, or mismatch arguments."""
    rng = random.Random(seed_for(cfg['seed'], 'train', regime, history))
    n = cfg['population']
    pop = [(0., 0., rng.uniform(0, math.pi)) for _ in range(n)]
    target = None
    for generation in range(cfg['training_generations']):
        if generation % cfg['environment_period'] == 0:
            angle = 0. if regime == 'structured' else rng.uniform(0, 2*math.pi)
            sign = rng.choice((-1., 1.))
            target = rotate((sign, 0.), angle)
        children = []
        for x, y, angle in pop:
            inherited = (angle + rng.gauss(0, cfg['orientation_sd'])) % math.pi
            dx, dy = proposal((rng.gauss(0, 1), rng.gauss(0, 1)), inherited,
                              cfg['major_sd'], cfg['minor_sd'])
            children.append((x+dx, y+dy, inherited))
        pop = select(pop + children, target, n)
    # Uniform individual, no alignment-based cherry-picking.
    chosen = pop[rng.randrange(n)]
    return chosen[2]


def predictor(angle, target, major, minor):
    """Pre-outcome directional variance difference; not a performance theorem."""
    direction = math.atan2(target[1], target[0])
    return (major*major-minor*minor)*math.cos(2*(angle-direction))


def transfer(cfg, angle, target, seed):
    """Matched zero starts; same normals; control proposals are quarter-turned.

    Frozen inherited rule; no further evolution of orientation during transfer.
    Endpoint is mean normalized squared-distance improvement of selected population.
    """
    rng = random.Random(seed)
    n = cfg['population']
    arms = [[(0., 0., angle + offset) for _ in range(n)]
            for offset in (0., math.pi/2)]
    initial = loss((0., 0.), target)
    if initial <= 0:
        raise ValueError('zero initial distance')
    trajectory = []
    for generation in range(cfg['test_generations']):
        normals = [(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(n)]
        for j in range(2):
            children = []
            for (x, y, a), z in zip(arms[j], normals):
                dx, dy = proposal(z, a, cfg['major_sd'], cfg['minor_sd'])
                children.append((x+dx, y+dy, a))
            arms[j] = select(arms[j] + children, target, n)
        scores = [1-sum(loss(p[:2], target) for p in arm)/(n*initial) for arm in arms]
        trajectory.append(scores)
    return trajectory


def assay(cfg):
    rows, histories = [], []
    for regime in ('structured', 'isotropic'):
        for history in range(cfg['histories_per_regime']):
            angle = train(cfg, regime, history)
            histories.append(dict(regime=regime, history=history, angle=angle))
            for family in list(cfg['mismatch_degrees']) + ['isotropic']:
                for task in range(cfg['tasks_per_family']):
                    rng = random.Random(seed_for(cfg['seed'], 'target', history, family, task))
                    direction = rng.uniform(0, 2*math.pi) if family == 'isotropic' else math.radians(family)
                    target = rotate((rng.choice((-1., 1.)), 0.), direction)
                    trajectory = transfer(cfg, angle, target,
                                          seed_for(cfg['seed'], 'transfer', history, family, task))
                    a, b = trajectory[-1]
                    rows.append(dict(regime=regime, history=history, family=str(family), task=task,
                                     angle=angle, target=list(target), predictor=predictor(
                                         angle, target, cfg['major_sd'], cfg['minor_sd']),
                                     organized=a, rotated=b, delta=a-b, trajectory=trajectory))
    return histories, rows


def mean(values):
    return math.fsum(values)/len(values)


def signed(value):
    return 0 if abs(value) <= 1e-12 else (1 if value > 0 else -1)


def crossing_record(grid, values):
    """Bracket adjacent non-ties; preserve intervening unresolved tie points."""
    signs = [signed(v) for v in values]
    nonzero = [i for i, sign in enumerate(signs) if sign]
    crossings = []
    for a, b in zip(nonzero, nonzero[1:]):
        if signs[a] == 1 and signs[b] == -1:
            crossings.append(dict(bracket=[grid[a], grid[b]],
                                  tie_points=[grid[i] for i in range(a+1, b)]))
    return dict(crossings=crossings, tie_points=[g for g,s in zip(grid,signs) if s==0])


def localization(predicted, observed):
    p, o = predicted['crossings'], observed['crossings']
    if not p and not o: return 'neither'
    if not p: return 'observed_only'
    if not o: return 'predicted_only'
    if len(p)>1 or len(o)>1: return 'multiple'
    if p[0]['tie_points'] or o[0]['tie_points']: return 'ambiguous_ties'
    return 'same_bracket' if p[0]['bracket']==o[0]['bracket'] else 'different_bracket'


def validate_config(cfg):
    for key in ('histories_per_regime','population','training_generations','environment_period',
                'test_generations','tasks_per_family','bootstrap_replicates','max_result_bytes'):
        if type(cfg[key]) is not int or cfg[key] <= 0: raise ValueError('invalid '+key)
    if cfg['histories_per_regime']<2 or cfg['bootstrap_replicates']<40:
        raise ValueError('insufficient inference configuration')
    for key in ('major_sd','minor_sd','orientation_sd'):
        if not math.isfinite(cfg[key]) or cfg[key]<=0: raise ValueError('invalid '+key)
    if cfg['major_sd']<cfg['minor_sd']: raise ValueError('principal SD ordering')
    grid=cfg['mismatch_degrees']
    if not grid or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=90 for v in grid):
        raise ValueError('invalid grid')
    if grid!=sorted(set(grid)) or type(cfg['seed']) is not int or cfg['max_attempts']!=1:
        raise ValueError('grid, seed or attempt constraint')


def validate_roster(cfg, rows):
    expected={(reg,h,str(f),t) for reg in ('structured','isotropic')
              for h in range(cfg['histories_per_regime'])
              for f in list(cfg['mismatch_degrees'])+['isotropic']
              for t in range(cfg['tasks_per_family'])}
    actual=[(r['regime'],r['history'],r['family'],r['task']) for r in rows]
    if len(actual)!=len(set(actual)) or set(actual)!=expected: raise ValueError('incomplete/duplicate roster')
    for r in rows:
        for key in ('predictor','organized','rotated','delta'):
            if not math.isfinite(r[key]): raise ValueError('nonfinite '+key)
        if abs(r['delta']-(r['organized']-r['rotated']))>1e-12: raise ValueError('delta mismatch')
        if any(not 0<=r[k]<=1+1e-12 for k in ('organized','rotated')): raise ValueError('score bounds')
        if len(r['trajectory'])!=cfg['test_generations'] or any(
            len(pair)!=2 or any(not math.isfinite(v) or not -1e-12<=v<=1+1e-12 for v in pair)
            for pair in r['trajectory']): raise ValueError('invalid trajectory')
        if any(abs(x-y)>1e-12 for x,y in zip(r['trajectory'][-1],(r['organized'],r['rotated']))):
            raise ValueError('endpoint mismatch')

def summarize(cfg, rows):
    """Whole-history bootstrap: tasks never treated as independent histories."""
    results = []
    for regime in ('structured', 'isotropic'):
        for family in list(map(str, cfg['mismatch_degrees'])) + ['isotropic']:
            group = [r for r in rows if r['regime'] == regime and r['family'] == family]
            clusters = [[r for r in group if r['history'] == h]
                        for h in range(cfg['histories_per_regime'])]
            deltas = [mean([r['delta'] for r in cluster]) for cluster in clusters]
            predictions = [mean([r['predictor'] for r in cluster]) for cluster in clusters]
            rng = random.Random(seed_for(cfg['seed'], 'bootstrap', regime, family))
            boot = sorted(mean([rng.choice(deltas) for _ in deltas])
                          for _ in range(cfg['bootstrap_replicates']))
            lo, hi = boot[int(.025*len(boot))], boot[int(.975*len(boot))]
            results.append(dict(regime=regime, family=family, mean_delta=mean(deltas),
                                exploratory_pointwise_95_interval=[lo, hi],
                                classification=('benefit' if lo > 0 else 'harm' if hi < 0 else 'inconclusive'),
                                mean_predictor=mean(predictions), history_deltas=deltas,
                                history_predictions=predictions,
                                sign_accuracy=mean([float(signed(p)==signed(d)) if signed(p) and signed(d) else .5
                                                    for p, d in zip(predictions, deltas)]),
                                always_benefit_accuracy=mean([float(signed(d)>0) if signed(d) else .5 for d in deltas]),
                                always_harm_accuracy=mean([float(signed(d)<0) if signed(d) else .5 for d in deltas]),
                                organized_ceiling_fraction=mean([float(r['organized']>.99) for r in group]),
                                rotated_ceiling_fraction=mean([float(r['rotated']>.99) for r in group]),
                                both_ceiling_fraction=mean([float(r['organized']>.99 and r['rotated']>.99) for r in group]),
                                mean_organized=mean([r['organized'] for r in group]),
                                mean_rotated=mean([r['rotated'] for r in group]),
                                ceiling_fraction=mean([float(r['organized']>.99 or r['rotated']>.99) for r in group])))
    brackets = []
    for regime in ('structured', 'isotropic'):
        panel = [r for r in results if r['regime']==regime and r['family']!='isotropic']
        for h in range(cfg['histories_per_regime']):
            grid=[r['family'] for r in panel]
            observed=crossing_record(grid,[r['history_deltas'][h] for r in panel])
            predicted=crossing_record(grid,[r['history_predictions'][h] for r in panel])
            brackets.append(dict(regime=regime, history=h, predicted=predicted, observed=observed,
                                 agreement=localization(predicted,observed)))
    agreement={}
    for regime in ('structured','isotropic'):
        group=[r for r in brackets if r['regime']==regime]
        agreement[regime]=dict(denominator=len(group),counts={
            name:sum(r['agreement']==name for r in group) for name in
            ('neither','observed_only','predicted_only','multiple','ambiguous_ties','same_bracket','different_bracket')})
    return dict(contrasts=results, reversal_brackets=brackets, localization_agreement=agreement,
                warning='Exploratory pointwise intervals; no multiplicity-controlled or meaningful-effect claim.')
