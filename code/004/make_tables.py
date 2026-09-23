from pathlib import Path
import json
P=Path(__file__).resolve().parent;s=json.loads((P/'summary.json').read_text())
for filename,diagnostic in [('ENDPOINT_TABLES.md',False),('DIAGNOSTIC_TABLES.md',True)]:
 lines=['# '+('Complete endpoint levels and contrasts' if not diagnostic else 'Complete choice, error and prediction diagnostics'),'','Every regime, family (including uniform reference), and early arm is retained. ALL/BOTH denotes equal averaging over all eight families and both early arms within each of 24 histories. Intervals reuse the same frozen regime-level bootstrap draws. They are paired, pointwise and exploratory.','','HINDSIGHT is a realized maximum, not an attainable policy or unbiased optimal-policy estimate. HALF is expected random choice, not a mixed population.']
 for g in s['groups']:
  lines+=['',f"## {g['regime']} / {g['family']} / early {g['early']}",'','| Metric | Mean | Pointwise 95% interval | Relative to zero | Relative to .02 target |','|---|---:|---|---|---|']
  for k,v in g['values'].items():
   isdiag=any(x in k for x in ['choose_O','tie','predicted','observed','decision_error','sign_accuracy','disagreement'])
   if isdiag!=diagnostic:continue
   lines.append(f"| {k} | {v['mean']:+.8f} | [{v['ci95'][0]:+.8f},{v['ci95'][1]:+.8f}] | {v['zero_classification']} | {v.get('target_classification','not applicable')} |")
 (P/filename).write_text('\n'.join(lines)+'\n')
(P/'HISTORY_SUMMARIES.json').write_text(json.dumps(s['histories'],indent=2)+'\n')
