"""Outcome-independent row-space sampler and frozen contrast algebra for064.

No scientific input is read and no population continuation is implemented here.
"""
import hashlib,math,random

MASTER=2026092564
BOOTSTRAP_SEED=2026092565
FAMILIES=('0','15','30','45','60','75','90','isotropic')
CELLS=('NATIVE_OO','NATIVE_OR','NATIVE_RO','NATIVE_RR','SHAPE_OO','SHAPE_OR','SHAPE_RO','SHAPE_RR')
def seed_for(h,f,t):
    s='|'.join(map(str,(MASTER,'state-shape064-row-orthogonal',h,f,t)))
    return int(hashlib.sha256(s.encode()).hexdigest()[:16],16)
def dot(a,b):return math.fsum(x*y for x,y in zip(a,b))
def helmert(n):
    return [[(1/math.sqrt((j+1)*(j+2)) if i<=j else -(j+1)/math.sqrt((j+1)*(j+2)) if i==j+1 else 0.) for j in range(n-1)] for i in range(n)]
def positive_qr(g):
    """Two-pass modified Gram-Schmidt; positive R diagonals, no pivot/redraw."""
    n=len(g);assert n and all(len(row)==n for row in g)
    columns=[]
    for j in range(n):
        v=[g[i][j] for i in range(n)]
        for _ in range(2):
            for q in columns:
                c=dot(q,v);v=[x-c*y for x,y in zip(v,q)]
        norm=math.sqrt(dot(v,v))
        if not math.isfinite(norm) or norm<=0:raise ValueError('Degenerate Gaussian QR input; no redraw')
        columns.append([x/norm for x in v])
    q=[[columns[j][i] for j in range(n)] for i in range(n)]
    error=max(abs(dot(columns[i],columns[j])-(1. if i==j else 0.)) for i in range(n) for j in range(n))
    if error>2e-12:raise ValueError('Orthogonality tolerance exceeded; no redraw')
    return q
def sample_q(seed,n=32):
    rng=random.Random(seed);g=[[rng.gauss(0.,1.) for _ in range(n-1)] for _ in range(n-1)]
    return positive_qr(g)
def reshape(points,q):
    n=len(points);assert n>=2 and len(q)==n-1 and all(len(row)==n-1 for row in q)
    u=helmert(n);mu=[math.fsum(p[k] for p in points)/n for k in (0,1)]
    d=[[p[k]-mu[k] for k in (0,1)] for p in points]
    z=[[math.fsum(u[i][j]*d[i][k] for i in range(n)) for k in (0,1)] for j in range(n-1)]
    qz=[[math.fsum(q[i][j]*z[j][k] for j in range(n-1)) for k in (0,1)] for i in range(n-1)]
    return [[mu[k]+math.fsum(u[i][j]*qz[j][k] for j in range(n-1)) for k in (0,1)] for i in range(n)]
def metrics(y):
    out={key:y[key] for key in CELLS}
    for state in ('O','R'):
        for shape in ('NATIVE','SHAPE'):out['F_'+state+'_'+shape]=y[shape+'_'+state+'O']-y[shape+'_'+state+'R']
    for shape in ('NATIVE','SHAPE'):out['J_'+shape]=out['F_O_'+shape]-out['F_R_'+shape]
    for pair in ('OO','OR','RO','RR'):out['G_'+pair]=y['NATIVE_'+pair]-y['SHAPE_'+pair]
    out['DELTA']=out['J_NATIVE']-out['J_SHAPE']
    out['G_MEAN']=sum(out['G_'+pair] for pair in ('OO','OR','RO','RR'))/4
    assert len(out)==20
    return out
