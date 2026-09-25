"""Separate arithmetic audit; imports no new producer/operator/sampler/analysis code.
Run after production. Fixed h0 raw block only; all initial moments and380estimates.
This executor-supplied checker does not assert independent supervisor acceptance.
"""
import json,gzip,math,random,struct,pathlib,hashlib,collections
P=pathlib.Path(__file__).resolve().parent
F=('0','15','30','45','60','75','90','isotropic');R=('structured','isotropic');C=('OO','OR','RO','RR');CELLS=tuple(s+'_'+c for s in ('NATIVE','SHAPE') for c in C)
def read(n):return json.loads((P/n).read_text())
def rows(n):
 with gzip.open(P/n,'rt') as f:
  for line in f:yield json.loads(line)
def tuples(x):return tuple(map(tuples,x)) if isinstance(x,list) else x
def dot(a,b):return math.fsum(x*y for x,y in zip(a,b))
def loss(p,t,h):
 x,y=p[0]-t[0],p[1]-t[1];return (h[0][0]*x*x+2*h[0][1]*x*y+h[1][1]*y*y)/(h[0][0]*t[0]*t[0]+2*h[0][1]*t[0]*t[1]+h[1][1]*t[1]*t[1])
def moment(p,t,h):
 mu=[sum(x[k] for x in p)/32 for k in (0,1)];cov=[sum((x[i]-mu[i])*(x[j]-mu[j]) for x in p)/32 for i in (0,1) for j in (0,1)];meanloss=sum(loss(x,t,h) for x in p)/32
 return mu+cov+[meanloss]
def q_at(seed):
 r=random.Random(seed);a=[[r.gauss(0.,1.) for j in range(31)] for i in range(31)];cols=[]
 for j in range(31):
  v=[a[i][j] for i in range(31)]
  for repeat in range(2):
   for c in cols:
    proj=dot(c,v);v=[x-proj*y for x,y in zip(v,c)]
  norm=math.sqrt(dot(v,v));assert norm>0 and math.isfinite(norm);cols.append([x/norm for x in v])
 return [list(v) for v in zip(*cols)]
def reshape(p,q):
 u=[[1/math.sqrt((j+1)*(j+2)) if i<=j else -(j+1)/math.sqrt((j+1)*(j+2)) if i==j+1 else 0. for j in range(31)] for i in range(32)]
 mu=[math.fsum(x[k] for x in p)/32 for k in (0,1)];d=[[x[k]-mu[k] for k in (0,1)] for x in p];z=[[math.fsum(u[i][j]*d[i][k] for i in range(32)) for k in (0,1)] for j in range(31)];v=[[math.fsum(q[i][j]*z[j][k] for j in range(31)) for k in (0,1)] for i in range(31)]
 return [[mu[k]+math.fsum(u[i][j]*v[j][k] for j in range(31)) for k in (0,1)] for i in range(32)]
def step(pop,t,angle,z,us,h):
 ca,sa=math.cos(angle),math.sin(angle);children=[]
 for p,(a,b) in zip(pop,z):
  dx=.12*a;dy=.02*b;children.append((p[0]+(ca*dx-sa*dy),p[1]+(sa*dx+ca*dy)))
 candidates=list(pop)+children;ls=[loss(p,t,h) for p in candidates];remaining=list(range(64));ids=[]
 for u in us:
  best=min(ls[i] for i in remaining);weights=[math.exp(-10.*(ls[i]-best)) for i in remaining];threshold=u*math.fsum(weights);total=0.;chosen=None
  for k,w in enumerate(weights):
   total+=w
   if w>0 and threshold<total:chosen=k;break
  if chosen is None:chosen=max(k for k,w in enumerate(weights) if w>0)
  ids.append(remaining.pop(chosen))
 return [candidates[i] for i in ids],ids

def main():
 cfg=read('native_config002.json')['transfer'];h=cfg['metric_matrix'];roster=read('roster.json');maxmoment=maxraw=maxscore=maxq=0.;updates=0
 with gzip.open(P/'Q.bin.gz','rb') as f:qb=f.read()
 qs={}
 for i in range(64):
  family=F[i//8];task=i%8;seed=int(hashlib.sha256(('2026092564|state-shape064-row-orthogonal|0|'+family+'|'+str(task)).encode()).hexdigest()[:16],16);q=q_at(seed);flat=struct.unpack_from('<961d',qb,i*7688);err=max(abs(x-y) for x,y in zip((v for r in q for v in r),flat));assert err<=1e-12;maxq=max(maxq,err);qs[i]=q
 coordinates={};indices={}
 for r in R:
  with gzip.open(P/('raw/'+r+'-h00.coords.gz'),'rb') as f:coordinates[r]=f.read()
  with gzip.open(P/('raw/'+r+'-h00.indices.gz'),'rb') as f:indices[r]=f.read()
 measurement=rows('MEASUREMENTS.jsonl.gz');n=0
 with gzip.open(P/'SHAPED_INITIAL.bin.gz','rb') as initial:
  for n,cp in enumerate(rows('checkpoints.jsonl.gz')):
   row=roster[n];meas=next(measurement);assert meas['row_index']==n;flat=struct.unpack('<128d',initial.read(1024));shaped={s:[flat[si*64+j*2:si*64+j*2+2] for j in range(32)] for si,s in enumerate(('O','R'))}
   for s in ('O','R'):
    a,b=moment(cp['populations'][s],row['target'],h),moment(shaped[s],row['target'],h);err=max(abs(x-y) for x,y in zip(a,b));assert err<=1e-12;maxmoment=max(maxmoment,err)
   if row['history']!=0:continue
   local=F.index(row['family'])*8+row['task'];regime=row['regime'];pops={}
   for s in ('O','R'):
    expected=reshape(cp['populations'][s],qs[local]);err=max(abs(x-y) for a,b in zip(expected,shaped[s]) for x,y in zip(a,b));assert err<=1e-12;maxraw=max(maxraw,err)
   for c in C:pops[c]=list(shaped[c[0]])
   mut=random.Random();sur=random.Random();mut.setstate(tuples(cp['mutation_random_state']));sur.setstate(tuples(cp['survival_random_state']))
   for g in range(21):
    if g:
     z=[(mut.gauss(0,1),mut.gauss(0,1)) for _ in range(32)];us=[sur.random() for _ in range(32)]
     for ci,c in enumerate(C):
      pops[c],ids=step(pops[c],row['target'],row['angle']+(math.pi/2 if c[1]=='R' else 0.),z,us,h);off=local*2560+(g-1)*128+ci*32;assert bytes(ids)==indices[regime][off:off+32],(n,g,c,'survivors');updates+=1
    data=struct.unpack_from('<256d',coordinates[regime],local*43008+g*2048)
    for ci,c in enumerate(C):
     expected=[x for p in pops[c] for x in p];observed=data[ci*64:(ci+1)*64];err=max(abs(a-b) for a,b in zip(expected,observed));assert err<=1e-12,(n,g,c,err);maxraw=max(maxraw,err);err=abs((1-sum(loss(p,row['target'],h) for p in pops[c])/32)-meas['trajectory'][g]['SHAPE_'+c]['performance']);assert err<=1e-12;maxscore=max(maxscore,err)
  assert initial.read()==b''
 assert n+1==3072 and next(measurement,None) is None and updates==10240
 # Independent linear coefficient construction; no producer metric helper.
 coefficients={c:[int(c==d) for d in CELLS] for c in CELLS}
 def combine(name,parts):coefficients[name]=[sum(weight*coefficients[c][i] for c,weight in parts) for i in range(8)]
 for s in ('O','R'):
  for shape in ('NATIVE','SHAPE'):combine('F_'+s+'_'+shape,[(shape+'_'+s+'O',1),(shape+'_'+s+'R',-1)])
 for shape in ('NATIVE','SHAPE'):combine('J_'+shape,[('F_O_'+shape,1),('F_R_'+shape,-1)])
 for c in C:combine('G_'+c,[('NATIVE_'+c,1),('SHAPE_'+c,-1)])
 combine('DELTA',[('G_OO',1),('G_OR',-1),('G_RO',-1),('G_RR',1)]);combine('G_MEAN',[('G_'+c,.25) for c in C])
 by={};stored_controls=rows('outcomes.jsonl.gz');maxstatistics=0.
 for row in rows('PAIR_ENDPOINTS.jsonl.gz'):
  control=next(stored_controls)
  for c in C:assert row['cells']['NATIVE_'+c]==control['endpoints'][c]
  y=[row['cells'][c] for c in CELLS];v={m:math.fsum(a*b for a,b in zip(coef,y)) for m,coef in coefficients.items()}
  for m in v:assert abs(v[m]-row['metrics'][m])<=1e-12
  by.setdefault((row['regime'],row['history'],row['family']),[]).append(v)
 assert len(by)==384 and all(len(v)==8 for v in by.values()) and next(stored_controls,None) is None
 groups={r+'|'+f:[{m:math.fsum(v[m] for v in by[r,history,f])/8 for m in coefficients} for history in range(24)] for r in R for f in F}
 for r in R:groups[r+'|ALL8']=[{m:math.fsum(groups[r+'|'+f][history][m] for f in F)/8 for m in coefficients} for history in range(24)]
 groups['structured_MINUS_isotropic|ALL8']=[{m:groups['structured|ALL8'][history][m]-groups['isotropic|ALL8'][history][m] for m in coefficients} for history in range(24)]
 bootstrap=read('BOOTSTRAP.json');rng=random.Random(2026092565);assert bootstrap==[[rng.randrange(24) for _ in range(24)] for _ in range(2000)];counts=[collections.Counter(v) for v in bootstrap];est=read('ESTIMATES.json');checked=0
 def quantile(v,q):
  z=1999*q;i=int(z);return v[i]*(1-(z-i))+v[i+1]*(z-i)
 for group,histories in groups.items():
  for metric in coefficients:
   values=[v[metric] for v in histories];samples=sorted(math.fsum(values[i]*n for i,n in counter.items())/24 for counter in counts);ci=[quantile(samples,.025),quantile(samples,.975)];mean=math.fsum(values)/24;record=est[group+'|'+metric];err=max(abs(mean-record['mean']),*(abs(x-y) for x,y in zip(ci,record['ci95'])));assert err<=1e-12;maxstatistics=max(maxstatistics,err);assert record['classification']==('positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved');checked+=1
 assert checked==380 and len(est)==380
 result=dict(status='PASS',scope='Executor-supplied independent-arithmetic checker; supervisor acceptance separate',initial_states=6144,raw_roster_rows=128,raw_paths=512,raw_updates=updates,candidate_scores=updates*64,sampler_matrices=64,estimates=checked,maximum_errors=dict(initial_moments=maxmoment,raw_traits=maxraw,raw_scores=maxscore,sampler=maxq,statistics=maxstatistics))
 (P/'AUDIT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
