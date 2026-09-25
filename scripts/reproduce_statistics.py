"""Recompute archived statistical grids, without running population dynamics."""
from pathlib import Path
import json,argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);args=parser.parse_args();root=args.root
    reports=[]
    for study in read(root/'provenance/STUDIES.json'):
        ident=study['study'];p=root/'results'/ident;s=read(p/('ESTIMATES.json' if ident=='064' else 'summary.json'));count=0;err=0.
        def compare(x,ids,expected,order=False):
            nonlocal count,err
            a=np.asarray(x,float);idx=np.asarray(ids,int);assert len(a)==24 and idx.shape==(2000,24)
            # Preserve the original sequential averaging; differences are bounded below.
            boot=a[idx].mean(axis=1)
            ci=np.sort(boot)[[50,1950]] if order else np.quantile(boot,[.025,.975],method='linear')
            delta=max(abs(float(a.mean())-expected[0]),max(abs(ci-np.asarray(expected[1]))))
            assert delta<2e-13,(ident,count,delta,expected)
            err=max(err,float(delta));count+=1
        if ident=='064':
            groups=read(p/'GROUP_TABLE.json');ids=read(p/'BOOTSTRAP.json')
            histories=read(p/'HISTORY_TABLE.json');bykey={(q['regime'],q['history'],q['family']):q['metrics'] for q in histories}
            names=('0','15','30','45','60','75','90','isotropic')
            for regime in ('structured','isotropic'):
                for h in range(24):
                    for metric in groups[regime+'|ALL8'][h]:
                        mean=sum(bykey[regime,h,f][metric] for f in names)/8
                        assert abs(mean-groups[regime+'|ALL8'][h][metric])<2e-13
                        direct=groups['structured|ALL8'][h][metric]-groups['isotropic|ALL8'][h][metric]
                        assert abs(direct-groups['structured_MINUS_isotropic|ALL8'][h][metric])<2e-13
            for key,q in s.items():
                group,metric=key.rsplit('|',1)
                compare([row[metric] for row in groups[group]],ids,(q['mean'],q['ci95']))
                ci=q['ci95'];assert q['classification']==('positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved')
            assert count==380
        elif 'values' in s:
            rows=sorted([json.loads(l) for l in (p/'BLOCK_SUMMARIES.jsonl').read_text().splitlines()],key=lambda x:x['block']);ids=read(p/'BOOTSTRAP_INDICES.json')
            assert all(set(row['values'])==set(s['values']) for row in rows)
            for k,v in s['values'].items():compare([row['values'][k] for row in rows],ids,(v['mean'],v['ci95']))
        elif ident.startswith('V'):
            ids=read(p/'REPLAYED_BOOTSTRAP_INDICES.json')
            for g in s['contrasts']:
                ci=g.get('pointwise_95_interval',g.get('exploratory_pointwise_95_interval'))
                compare(g['history_deltas'],ids[g['regime']+'|'+g['family']],(g['mean_delta'],ci),True)
        else:
            groups=s.get('families',s.get('groups'));ids=read(p/('BOOTSTRAP_INDICES.json' if ident in ['004','005'] else 'REPLAYED_BOOTSTRAP_INDICES.json'))
            dims=['regime','family']+(['early'] if 'groups' in s else [])
            lookup={}
            for h in s['histories']:lookup.setdefault(tuple(h[k] for k in dims),[]).append(h)
            for g in groups:
                hh=sorted(lookup[tuple(g[k] for k in dims)],key=lambda h:h['history'])
                ix=ids[g['regime']] if ident in ['004','005'] else ids[g['regime']+'|'+g['family']]
                for k,v in g['values'].items():compare([h['values'][k] for h in hh],ix,(v['mean'],v['ci95']))
        reports.append({'study':ident,'mean_interval_pairs':count,'maximum_absolute_discrepancy':err})
    result={'status':'PASS','studies':reports,'total_mean_interval_pairs':sum(x['mean_interval_pairs'] for x in reports),'maximum_absolute_discrepancy':max(x['maximum_absolute_discrepancy'] for x in reports),'new_population_paths':0,'new_random_draws':0,'scope':'Recomputation from included history/block aggregates and bootstrap rows. Original early bootstrap seeds were replayed during packaging and saved as rows. Does not reconstruct omitted raw trajectories or imply independent model validation.'}
    (root/'provenance/STATISTICS_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
