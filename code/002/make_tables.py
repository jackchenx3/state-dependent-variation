from pathlib import Path
import json
P=Path(__file__).resolve().parent;s=json.loads((P/'summary.json').read_text())
lines=['# Complete generation-25 four-cell and contrast tables','','All 16 historical-regime × target-family groups are retained. Values are normalized performance units; parentheses contain paired pointwise exploratory 95% whole-history bootstrap intervals. Each family has 24 histories, with eight paired trials averaged per history. Uniform-direction references appear as `isotropic` families. No multiplicity adjustment or equivalence inference.','','OO/OR/RO/RR denote early state then later rule. Every conditional contrast subtracts R from O for the named factor. Symmetric rule+state=OO−RR by definition.']
for g in s['families']:
 lines+=['',f"## {g['regime']}: {g['family']}",'','| Cell / contrast | Mean | Pointwise 95% interval | Sign classification |','|---|---:|---|---|']
 for k,v in g['values'].items():lines.append(f"| {k} | {v['mean']:+.8f} | [{v['ci95'][0]:+.8f}, {v['ci95'][1]:+.8f}] | {v['classification']} |")
(P/'ENDPOINT_TABLES.md').write_text('\n'.join(lines)+'\n')
lines=['# Per-history endpoint values and contrasts','','Every history-family comparison is retained after averaging eight paired trials. These are descriptive estimates without per-history confidence intervals. Full trial outcomes and component trajectories are in outcomes.jsonl.gz.','','| Regime | Family | History | OO | OR | RO | RR | Rule given O | Rule given R | State given O | State given R | Interaction | Rule | State | Original |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
keys=list(s['families'][0]['values'])
for r in s['histories']:lines.append('| '+r['regime']+' | '+r['family']+' | '+str(r['history'])+' | '+' | '.join(f"{r['values'][k]:+.8f}" for k in keys)+' |')
(P/'HISTORY_TABLE.md').write_text('\n'.join(lines)+'\n')
