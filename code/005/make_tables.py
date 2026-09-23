from pathlib import Path
import json,gzip
P=Path(__file__).resolve().parent;S=json.loads((P/'summary.json').read_text());intro='All means and paired whole-history 95% intervals use the fixed checkpoint panel and shared regime-specific resamples. Conditional ranking intervals are separate 97.5% marginal paired-replicate intervals. Frequencies describe this classification procedure; unresolved is not absence. No refitted or reselected policy.\n';out=['# Complete calibration and performance diagnostics\n',intro];ranks=['# Complete conditional ranking counts and frequencies\n',intro]
for g in S['groups']:
 label='\n## '+g['regime']+' / '+g['family']+' / early '+g['early']+'\n';out.extend([label,'| Quantity | Mean | Pointwise 95% interval | Relative to zero |','|---|---:|---|---|']);ranks.extend([label,'Checkpoint denominator: '+str(g['checkpoint_count'])+'\n','| Quantity | Count | Frequency | Pointwise history 95% interval |','|---|---:|---:|---|'])
 for k,v in g['values'].items():
  if k in g['counts']:ranks.append('| %s | %d | %.8f | [%.8f, %.8f] |'%(k,g['counts'][k],v['mean'],*v['ci95']))
  else:out.append('| %s | %+.9f | [%+.9f, %+.9f] | %s |'%(k,v['mean'],*v['ci95'],v['zero_classification']))
(P/'DIAGNOSTIC_TABLES.md').write_text('\n'.join(out)+'\n');(P/'RANKING_TABLES.md').write_text('\n'.join(ranks)+'\n');(P/'HISTORY_SUMMARIES.json').write_text(json.dumps(S['histories'],indent=2)+'\n')
