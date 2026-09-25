"""All prespecified estimates, adverse outcomes and descriptive moment divergence."""
from common import *
from analysis064 import *

def main():
 pairs=list(rows('PAIR_ENDPOINTS.jsonl.gz'));histories,groups=aggregate(pairs);estimates=estimate(groups,read('BOOTSTRAP.json'))
 native_error=0.
 for original in read('native_summary002.json')['families']:
  for cell in ('OO','OR','RO','RR'):
   key=original['regime']+'|'+original['family']+'|NATIVE_'+cell;native_error=max(native_error,abs(estimates[key]['mean']-original['values'][cell]['mean']))
 assert native_error<=1e-12
 save('NATIVE_MEAN_CHECK.json',dict(status='PASS',means=64,maximum_error=native_error,old_intervals_not_reused=True))
 save('HISTORY_TABLE.json',[dict(regime=k[0],history=k[1],family=k[2],metrics=v) for k,v in histories.items()]);save('GROUP_TABLE.json',groups);save('ESTIMATES.json',estimates)
 max_errors={};n=0
 for q in rows('MOMENT_CHECKS.jsonl.gz'):
  n+=1
  for k,v in q['errors'].items():max_errors[k]=max(max_errors.get(k,0.),v)
 assert n==6144 and max(max_errors.values())<=1e-12
 cells=CELLS;declines={c:0 for c in cells};negative={c:0 for c in cells};endpoint_negative={c:0 for c in cells};diagnostics=[]
 sums=[dict(generation=g,centroid_max_difference=0.,covariance_max_difference=0.,mean_absolute_performance_difference=0.) for g in range(5,26)]
 for row in rows('MEASUREMENTS.jsonl.gz'):
  trajectory=row['trajectory']
  for j,record in enumerate(trajectory):
   for c in cells:
    negative[c]+=record[c]['performance']<0
    if j:declines[c]+=record[c]['performance']<trajectory[j-1][c]['performance']
   for c in ('OO','OR','RO','RR'):
    a,b=record['NATIVE_'+c],record['SHAPE_'+c];sums[j]['centroid_max_difference']=max(sums[j]['centroid_max_difference'],*(abs(x-y) for x,y in zip(a['centroid'],b['centroid'])));sums[j]['covariance_max_difference']=max(sums[j]['covariance_max_difference'],*(abs(a['covariance'][x][y]-b['covariance'][x][y]) for x in (0,1) for y in (0,1)));sums[j]['mean_absolute_performance_difference']+=abs(a['performance']-b['performance'])/(3072*4)
  for c in cells:endpoint_negative[c]+=trajectory[-1][c]['performance']<0
 primary=estimates[PRIMARY];status={'negative':'supports_directional_prediction','positive':'contradicts_directional_prediction','unresolved':'unresolved'}[primary['classification']]
 save('DIAGNOSTICS.json',dict(initial_moment_checks=n,maximum_initial_errors=max_errors,generations=sums,declining_updates=declines,negative_measurements=negative,negative_endpoints=endpoint_negative))
 save('VALIDATION_CHECK.json',dict(status='PASS',scientific_status=status,primary=PRIMARY,primary_estimate=primary,estimates=len(estimates),new_paths=12288,controls_replayed=0,notes='Pointwise exploratory intervals; unresolved is not equivalence. Negative performance and declines retained.'))
if __name__=='__main__':main()
