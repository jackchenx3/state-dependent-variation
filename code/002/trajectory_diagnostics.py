"""Descriptive negative/decline counts from retained trajectories, no simulation."""
from pathlib import Path
import json,gzip
p=Path(__file__).resolve().parent
out={k:dict(negative_trajectories=0,negative_endpoints=0,declining_trajectories=0,declining_transitions=0,minimum_performance=1.) for k in ['OO','OR','RO','RR']}
with gzip.open(p/'outcomes.jsonl.gz','rt') as f:
    for line in f:
        row=json.loads(line)
        for cell,v in out.items():
            scores=[0.]+[g[cell]['performance'] for g in row['trajectory']]
            v['negative_trajectories']+=int(min(scores)<0);v['negative_endpoints']+=int(scores[-1]<0)
            n=sum(b<a-1e-12 for a,b in zip(scores,scores[1:]))
            v['declining_trajectories']+=int(n>0);v['declining_transitions']+=n
            v['minimum_performance']=min(v['minimum_performance'],min(scores))
(p/'TRAJECTORY_DIAGNOSTICS.json').write_text(json.dumps(out,indent=2)+'\n')
