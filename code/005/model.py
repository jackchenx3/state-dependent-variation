"""Independent diagnostic continuations from frozen actual populations."""
import math,random
from switch_model import set_rule,draws,advance
from v3_model import normalized_loss
CELLS=('OO','OR','RO','RR')
def initialize(cp):
    return {cell:set_rule(cp['populations'][cell[0]],cp['angle']+(math.pi/2 if cell[1]=='R' else 0.)) for cell in CELLS}
def performance(pop,target,h):return 1-sum(normalized_loss(x[:2],target,h) for x in pop)/len(pop)
def evaluate(cfg,cp,seeds):
    pops=initialize(cp);mut=random.Random(seeds['mutation_seed']);sur=random.Random(seeds['survival_seed']);trajectory=[];c=cfg['transfer']
    for generation in range(6,26):
        z,u=draws(mut,sur,c['population'])
        for cell in CELLS:pops[cell]=advance(pops[cell],cp['target'],c,z,u)
        trajectory.append([performance(pops[cell],cp['target'],c['metric_matrix']) for cell in CELLS])
    return trajectory
