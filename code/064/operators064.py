"""Source-bound002 continuation factorization adding only selected-index output."""
import math,random
from model import set_rule,draws,measure,advance
from baseline_model import proposal
from v2_model import sample_indices
from v3_model import normalized_loss
from shape064_reference import reshape,dot,helmert

def tuples(value):return tuple(tuples(x) for x in value) if isinstance(value,list) else value

def restore(checkpoint):
 mutation=random.Random();survival=random.Random();mutation.setstate(tuples(checkpoint['mutation_random_state']));survival.setstate(tuples(checkpoint['survival_random_state']));return mutation,survival

def advance_indices(pop,target,cfg,normals,uniforms):
 children=[]
 for (x,y,a),z in zip(pop,normals):
  dx,dy=proposal(z,a,cfg['major_sd'],cfg['minor_sd']);children.append((x+dx,y+dy,a))
 candidates=pop+children;losses=[normalized_loss(p[:2],target,cfg['metric_matrix']) for p in candidates];indices=sample_indices(losses,uniforms,cfg['selection_coefficient'])
 return [candidates[i] for i in indices],indices

def orthogonality(q):
 assert len(q)==31 and all(len(r)==31 and all(math.isfinite(x) for x in r) for r in q)
 columns=list(zip(*q));column_error=max(abs(dot(columns[i],columns[j])-int(i==j)) for i in range(31) for j in range(31));row_error=max(abs(dot(q[i],q[j])-int(i==j)) for i in range(31) for j in range(31))
 assert max(column_error,row_error)<=2e-12,'Q orthogonality failure; no redraw'
 return dict(qtq_error=column_error,qqt_error=row_error)

def basis_check():
 u=helmert(32);cols=list(zip(*u));zero=max(abs(math.fsum(c)) for c in cols);error=max(abs(dot(cols[i],cols[j])-int(i==j)) for i in range(31) for j in range(31));assert max(zero,error)<=2e-12;return dict(column_sum_error=zero,orthogonality_error=error)

def transform(pop,q,target,h):
 before=measure(pop,target,h);points=reshape([p[:2] for p in pop],q);assert all(math.isfinite(x) for p in points for x in p)
 shaped=[(p[0],p[1],old[2]) for p,old in zip(points,pop)];after=measure(shaped,target,h)
 errors=dict(centroid=max(abs(a-b) for a,b in zip(before['centroid'],after['centroid'])),covariance=max(abs(before['covariance'][i][j]-after['covariance'][i][j]) for i in (0,1) for j in (0,1)),normalized_loss=abs(before['performance']-after['performance']),source_identity=before['identity_error'],shape_identity=after['identity_error'])
 assert max(errors.values())<=1e-12,('Moment/score invariant failure; no omission or redraw',errors)
 return shaped,dict(source=before,shape=after,errors=errors)

def branches(shaped,phi):return {cell:set_rule(shaped[cell[0]],phi+(math.pi/2 if cell[1]=='R' else 0.)) for cell in ('OO','OR','RO','RR')}
def native_controls(record):
 assert len(record['trajectory'])==25
 return dict(endpoints={'NATIVE_'+c:record['endpoints'][c] for c in ('OO','OR','RO','RR')},trajectory=[{'NATIVE_'+c:record['trajectory'][g][c] for c in ('OO','OR','RO','RR')} for g in range(4,25)])
