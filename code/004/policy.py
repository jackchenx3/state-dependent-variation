"""Fixed one-time policies: centroid, Gaussian moments, empirical configuration.

Uses only the supplied current population, target, metric, candidate covariances,
and numerical tie convention. No seeds, regime labels or future data accepted.
"""
import math
ZERO=((0.,0.),(0.,0.))
def mv(a,x):return [a[i][0]*x[0]+a[i][1]*x[1] for i in (0,1)]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in (0,1)) for j in (0,1)] for i in (0,1)]
def dot(x,y):return x[0]*y[0]+x[1]*y[1]
def add(a,b):return [[a[i][j]+b[i][j] for j in (0,1)] for i in (0,1)]
def component(mean,cov,target,a,beta):
    # D need not be symmetric: preserve T A product order.
    ta=mm(cov,a);d=[[float(i==j)+2*beta*ta[i][j] for j in (0,1)] for i in (0,1)]
    det=d[0][0]*d[1][1]-d[0][1]*d[1][0]
    if det<=0:raise ValueError('invalid Gaussian determinant')
    k=[[d[1][1]/det,-d[0][1]/det],[-d[1][0]/det,d[0][0]/det]]
    r=[mean[i]-target[i] for i in (0,1)];kr=mv(k,r);v=mm(k,cov)
    logz=-.5*math.log(det)-beta*dot(r,mv(a,kr))
    q=dot(kr,mv(a,kr))+sum(a[i][j]*v[j][i] for i in (0,1) for j in (0,1))
    if not math.isfinite(logz) or not math.isfinite(q) or q < -1e-12:raise ValueError('invalid Gaussian prediction')
    return logz,q

def mixture(components):
    b=max(z for z,q in components);weights=[math.exp(z-b) for z,q in components]
    return math.fsum(w*q for w,(_,q) in zip(weights,components))/math.fsum(weights)

def moments(pop):
    n=len(pop);mu=[sum(p[i] for p in pop)/n for i in (0,1)]
    s=[[sum((p[i]-mu[i])*(p[j]-mu[j]) for p in pop)/n for j in (0,1)] for i in (0,1)]
    return mu,s

def choose(qo,qr,early,tol=1e-12):
    diff=qo-qr;tie=abs(diff)<=tol
    return dict(predicted_O_loss=qo,predicted_R_loss=qr,predicted_O_minus_R_loss=diff,choice=early if tie else ('O' if diff<0 else 'R'),tie=tie)

def decisions(pop,target,a,beta,covariances,early,tol=1e-12):
    mu,s=moments(pop);result={}
    for name in ('M','G','E'):
        values={}
        for rule,c in covariances.items():
            if name=='M':comps=[component(mu,ZERO,target,a,beta),component(mu,c,target,a,beta)]
            elif name=='G':comps=[component(mu,s,target,a,beta),component(mu,add(s,c),target,a,beta)]
            else:comps=[component(p[:2],t,target,a,beta) for p in pop for t in (ZERO,c)]
            values[rule]=mixture(comps)
        result[name]=dict(choose(values['O'],values['R'],early,tol),gaussian_component_evaluations=4 if name!='E' else 4*len(pop))
    return result
