from pathlib import Path
import json
P=Path(__file__).resolve().parent;s=json.loads((P/'summary.json').read_text())
lines=['# Complete generation-25 cells and prespecified contrasts','','All 16 regime/family groups, eight cells and 21 contrasts. Each group: 24 histories, eight paired trials averaged per history. Intervals are paired pointwise exploratory 95% whole-history bootstrap intervals (2,000 resamples). Unresolved does not mean equivalent to zero.','','Cell letters: centroid donor, COMPLETE centered-configuration donor, later rule. F_ms: later O−R; M_sr: centroid O−R; S_mr: configuration O−R. IM_s and IS_m are conditional feature-by-rule interactions. J_M and J_S average their respective two contexts. See PROTOCOL.md for exact formulas.']
for g in s['families']:
 lines+=['',f"## {g['regime']}: {g['family']}",'','| Cell / contrast | Mean | Pointwise 95% interval | Classification |','|---|---:|---|---|']
 for k,v in g['values'].items():lines.append(f"| {k} | {v['mean']:+.8f} | [{v['ci95'][0]:+.8f}, {v['ci95'][1]:+.8f}] | {v['classification']} |")
(P/'ENDPOINT_TABLES.md').write_text('\n'.join(lines)+'\n')
keys=list(s['families'][0]['values']);lines=['# All history-family estimates','','All 384 histories × family records (eight trials averaged per record); descriptive estimates without individual-history confidence intervals. Full precision in summary.json.','','| Regime | Family | History | '+' | '.join(keys)+' |','|---|---|---:|'+'---:|'*len(keys)]
for r in s['histories']:lines.append('| '+r['regime']+' | '+r['family']+' | '+str(r['history'])+' | '+' | '.join(f"{r['values'][k]:+.8f}" for k in keys)+' |')
(P/'HISTORY_TABLE.md').write_text('\n'.join(lines)+'\n')
