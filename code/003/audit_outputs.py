"""Independent stored-output arithmetic and interval audit; no model imports."""
from pathlib import Path
from itertools import zip_longest
from collections import defaultdict
import gzip,json,hashlib,math,random
P=Path(__file__).resolve().parent;checks=0
CELLS=tuple(m+s+r for m in 'OR' for s in 'OR' for r in 'OR');CONTROLS={'OOO':'OO','OOR':'OR','RRO':'RO','RRR':'RR'}
def check(condition,label):
    global checks
    checks+=1
    if not condition:raise AssertionError(label)
def avg(v):return sum(v)/len(v)
def close(a,b):return abs(a-b)<=1e-12
def effects(y):
    v={}
    for m in 'OR':
        for s in 'OR':v['F_'+m+s]=y[m+s+'O']-y[m+s+'R']
    for s in 'OR':
        for r in 'OR':v['M_'+s+r]=y['O'+s+r]-y['R'+s+r]
    for m in 'OR':
        for r in 'OR':v['S_'+m+r]=y[m+'O'+r]-y[m+'R'+r]
    # Derive interactions independently from conditional feature effects.
    for s in 'OR':v['IM_'+s]=v['M_'+s+'O']-v['M_'+s+'R']
    for m in 'OR':v['IS_'+m]=v['S_'+m+'O']-v['S_'+m+'R']
    v['three_factor']=v['IM_O']-v['IM_R'];v['I_joint']=y['OOO']-y['OOR']-y['RRO']+y['RRR'];v['J_M']=(v['IM_O']+v['IM_R'])/2;v['J_S']=(v['IS_O']+v['IS_R'])/2;v['J_M_minus_J_S']=v['J_M']-v['J_S'];return v
def quantile(x,p):
    v=sorted(x);z=(len(v)-1)*p;i=int(z);w=z-i;return v[i]*(1-w)+v[min(i+1,len(v)-1)]*w
cfg=json.loads((P/'config.json').read_text());summary=json.loads((P/'summary.json').read_text());roster=json.loads((P/'roster.json').read_text());h=cfg['transfer']['metric_matrix'];groups=defaultdict(list);sums={};counts=defaultdict(int);nrows=0;max_transform=0.;max_identity=0.;max_cov=0.;nonbit=0;minima={k:1. for k in CELLS};negative_final={k:0 for k in CELLS}
for mf in ['SOURCE_SHA256SUMS','RESULT_SHA256SUMS']:
    for line in (P/mf).read_text().splitlines():
        digest,file=line.split(None,1);check(hashlib.sha256((P/file.strip()).read_bytes()).hexdigest()==digest,'hash '+file)
with gzip.open(P/'outcomes.jsonl.gz','rt') as rf,gzip.open(P/'input_checkpoints.jsonl.gz','rt') as cf,gzip.open(P/'input_outcomes.jsonl.gz','rt') as bf:
    for fixed,rline,cline,bline in zip_longest(roster,rf,cf,bf):
        check(all(x is not None for x in (fixed,rline,cline,bline)),'complete roster rows');r=json.loads(rline);cp=json.loads(cline);old=json.loads(bline);nrows+=1
        for key,value in fixed.items():check(r[key]==value and cp[key]==value and old[key]==value,'roster '+key)
        check(r['generations']==list(range(5,26)) and len(r['trajectory'])==21,'no fictitious generations')
        mu={k:[avg([p[i] for p in cp['populations'][k]]) for i in (0,1)] for k in 'OR'}
        for cell in CELLS:
            m,s,rule=cell;pop=r['initial_populations'][cell];check(len(pop)==32,'initial N')
            center=[avg([p[i] for p in pop]) for i in (0,1)]
            cov=[[avg([(p[i]-center[i])*(p[j]-center[j]) for p in pop]) for j in (0,1)] for i in (0,1)]
            angle=r['angle']+(math.pi/2 if rule=='R' else 0)
            for a,b in zip(pop,cp['populations'][s]):
                check(a[2]==angle,'absolute rule')
                for i in (0,1):max_transform=max(max_transform,abs(a[i]-center[i]-(b[i]-mu[s][i])))
                if m==s:check(a[:2]==b[:2],'exact control coordinates')
            max_transform=max(max_transform,max(abs(center[i]-mu[m][i]) for i in (0,1)));check(max_transform<1e-12,'centroid and configuration')
            donor_cov=[[avg([(p[i]-mu[s][i])*(p[j]-mu[s][j]) for p in cp['populations'][s]]) for j in (0,1)] for i in (0,1)]
            max_cov=max(max_cov,max(abs(cov[i][j]-donor_cov[i][j]) for i in (0,1) for j in (0,1)));check(max_cov<1e-12,'donor covariance')
            check(center==r['trajectory'][0][cell]['centroid'] and cov==r['trajectory'][0][cell]['covariance'],'initial moments')
        target=r['target'];den=sum(target[i]*h[i][j]*target[j] for i in (0,1) for j in (0,1));key=(r['regime'],r['family']);counts[key]+=1
        if key not in sums:sums[key]=[{c:{m:0. for m in ('performance','centroid_loss','dispersion_loss')} for c in CELLS} for _ in range(21)]
        for g,rec in enumerate(r['trajectory']):
            for cell,mom in rec.items():
                d=[mom['centroid'][i]-target[i] for i in (0,1)];cent=sum(d[i]*h[i][j]*d[j] for i in (0,1) for j in (0,1))/den;spread=sum(h[i][j]*mom['covariance'][j][i] for i in (0,1) for j in (0,1))/den
                check(close(cent,mom['centroid_loss']) and close(spread,mom['dispersion_loss']),'quadratic components');error=abs(1-mom['performance']-cent-spread);max_identity=max(max_identity,error);check(error<1e-12,'loss identity');check(math.isfinite(mom['performance']) and mom['performance']<=1+1e-12,'valid performance')
                minima[cell]=min(minima[cell],mom['performance'])
                for name in sums[key][g][cell]:sums[key][g][cell][name]+=mom[name]
            for cell,prev in CONTROLS.items():
                value=rec[cell]['performance'];expected=old['trajectory'][g+4][prev]['performance'];check(close(value,expected),'control replay')
                if g>0:nonbit+=int(value!=expected)
        for cell in CELLS:check(r['endpoints'][cell]==r['trajectory'][-1][cell]['performance'],'endpoint');negative_final[cell]+=int(r['endpoints'][cell]<0)
        v=effects(r['endpoints'])
        for name,value in v.items():check(close(value,r['contrasts'][name]),'trial contrast '+name)
        check(close(v['three_factor'],v['IS_O']-v['IS_R']) and close(v['J_M']+v['J_S'],v['I_joint']),'factorial identities')
        groups[r['regime'],r['family'],r['history']].append(r['endpoints'])
check(nrows==3072,'3072 trials');history={}
for key,rows in groups.items():
    check(len(rows)==8,'eight paired trials');cells={k:avg([r[k] for r in rows]) for k in CELLS};history[key]=dict(cells,**effects(cells))
for row in summary['histories']:
    for name,v in history[row['regime'],row['family'],row['history']].items():check(close(v,row['values'][name]),'history mean')
rng=random.Random(2026092105);max_ci=0.
for group in summary['families']:
    key=(group['regime'],group['family']);hh=[history[key+(i,)] for i in range(24)];samples={k:[] for k in hh[0]}
    for b in range(2000):
        ids=[rng.randrange(24) for _ in range(24)]
        for k in samples:samples[k].append(avg([hh[i][k] for i in ids]))
    for name,v in group['values'].items():
        check(close(v['mean'],avg([r[name] for r in hh])),'family mean');ci=[quantile(samples[name],.025),quantile(samples[name],.975)];err=max(abs(a-b) for a,b in zip(ci,v['ci95']));max_ci=max(max_ci,err);check(err<1e-12,'interval')
        expected='positive' if ci[0]>0 else ('negative' if ci[1]<0 else 'unresolved');check(expected==v['classification'],'classification')
    for g in range(21):
        for cell in CELLS:
            for name,total in sums[key][g][cell].items():check(close(total/counts[key],group['mean_trajectories'][g][cell][name]),'mean trajectory')
acc=(P/'ACCOUNTING.psv').read_text().splitlines();parent=dict(zip(acc[0].split('|'),acc[1].split('|')));check(parent['State']=='COMPLETED' and parent['ExitCode']=='0:0' and parent['AllocCPUS']=='1' and parent['ReqMem']=='2G','accounting')
start=json.loads((P/'RUN_STARTED.json').read_text());end=json.loads((P/'COMPLETION.json').read_text());check(start['source_manifest_sha256']==hashlib.sha256((P/'SOURCE_SHA256SUMS').read_bytes()).hexdigest() and start['start_unix']<end['finish_unix'] and start['counterfactual_outcomes_started'] is False,'freeze ordering')
audit=dict(status='PASS',checks=checks,rows=nrows,original_non_bitwise_equal_values=nonbit,max_centroid_configuration_error=max_transform,max_covariance_error=max_cov,max_loss_identity_error=max_identity,max_interval_discrepancy=max_ci,minimum_recorded_performance=minima,negative_endpoints=negative_final,method='Independent streamed arithmetic and bootstrap audit; no experiment imports or transfer simulation. Contrasts recomputed via conditional feature effects.',discrepancies=[])
(P/'AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
