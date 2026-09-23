"""Deterministic presentation of completed results; never runs model simulation."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'result.json').read_text())
summary=r['summary']
contrasts=summary['contrasts']

def pct(x): return '{:.1f}%'.format(100*x)
def interval(c): return '[{:+.4f}, {:+.4f}]'.format(*c['exploratory_pointwise_95_interval'])

lines=['# Exploratory mismatch/reversal result', '',
'**Within this abstract model, the fixed geometric predictor located harmful transfer reasonably well.** Structured-history orientation had a positive population-performance contrast at sampled mismatches of 0, 15 and 30 degrees and a negative contrast at 60, 75 and 90 degrees. The 45-degree contrast was inconclusive. This is exploratory evidence of a conditional benefit-to-harm transition, not independent confirmation or a biological prediction.', '',
'## Execution and verification', '',
'- Slurm job **53276246** completed with exit **0:0** on **cn123**; 19 seconds elapsed, 18.283 parent-job CPU seconds. The script requested `norm`; scheduler accounting reports `short`. One CPU and 2 GiB were allocated/requested as recorded; batch MaxRSS was 36,000 KiB (about 35.2 MiB). No extra job or enlarged cohort was used.',
'- All **11 correctness tests passed** before scientific execution. All **48 independent histories** and **3,072 paired transfer trajectories** were retained; no failures, exclusions, tuning, replacement seeds, or reruns.',
'- Scientific model, tests and configuration are byte-identical to the previously reviewed package. Source/result hashes, compute runtime, tests, scheduler streams and terminal accounting are preserved.',
'- The latest explicit user instruction superseded the old project-local execution holds. `AUTHORIZATION.md` documents that change; it does not falsely certify the earlier all-writer site-cap requirement. The earlier implementation/reviews remain unchanged.', '',
'## Endpoint and full planned contrasts', '',
'Performance is the fraction of initial squared target distance removed after 25 generations. Each history contributes its mean over eight paired trials. Delta is organized minus quarter-turned spectrum-matched control. Thus +0.35 means 35 percentage points more normalized improvement; negative delta means **relative harm**, not deterioration from the starting population. Elitist selection improves both arms.', '',
'Intervals are predeclared **pointwise exploratory 95% whole-history bootstrap intervals** (24 histories/regime, 2,000 resamples). They are not multiplicity-adjusted. No practical-effect margin, equivalence result, or confirmatory p-value is claimed.', '',
'| Training history | Test mismatch | Mean delta | Pointwise 95% interval | Classification | Predictor sign accuracy |',
'|---|---:|---:|---|---|---:|']
for c in contrasts:
    lines.append('| {} | {} | {:+.4f} | {} | {} | {} |'.format(c['regime'],c['family'],c['mean_delta'],interval(c),c['classification'],pct(c['sign_accuracy'])))
lines += ['', 'The mean structured-history curve changes sign between 45 and 60 degrees, but the 45-degree interval crosses zero. The data support benefit at 30 degrees and harm at 60 degrees; they do not identify a statistically precise or universal crossing angle.', '',
'## Predictor validation and failures', '',
'The predictor was fixed before the run: directional variance advantage `(major_sd² − minor_sd²) cos(2 × (inherited angle − target direction))`. It uses the inherited rule and specified environmental direction, never the transfer outcome. This is prediction conditional on a known environment, not foresight about an unknown future target. It predicts the sign, not the magnitude, of the selected-population contrast.', '']
for regime in ('structured','isotropic'):
    panel=[c for c in contrasts if c['regime']==regime and c['family']!='isotropic']
    acc=sum(c['sign_accuracy'] for c in panel)/len(panel)
    benefit=sum(c['always_benefit_accuracy'] for c in panel)/len(panel)
    harm=sum(c['always_harm_accuracy'] for c in panel)/len(panel)
    loc=summary['localization_agreement'][regime]
    lines.append('- **{} histories:** grid sign agreement {} ({:.0f}/168 history-angle averages); always-benefit baseline {}, always-harm baseline {}. Localization across all {} histories: {}.'.format(regime,pct(acc),168*acc,pct(benefit),pct(harm),loc['denominator'],', '.join('{}={}'.format(k,v) for k,v in loc['counts'].items())))
lines += ['', '**Structured-history misses (zero-based IDs):**', '',
'| History | Predicted positive-to-negative interval | Observed interval |',
'|---:|---|---|']
for b in summary['reversal_brackets']:
    if b['regime']=='structured' and b['agreement']!='same_bracket':
        p=b['predicted']['crossings']; o=b['observed']['crossings']
        lines.append('| {} | {} | {} |'.format(b['history'],str(p[0]['bracket']) if p else 'none',str(o[0]['bracket']) if o else 'none'))
lines += ['',
'These 168 sign comparisons are correlated within 24 histories; they are not 168 independent replicates. Accuracy and crossing agreement are descriptive, without confidence intervals. A matching 15-degree grid interval is not an exact crossing estimate. The isotropic-history “neither” category means no positive-to-negative crossing detected on this grid; it is not a correctly localized crossing. Independent review found that all nine such histories have a negative-to-positive transition, which the predeclared harm-onset definition excludes. Structured histories span reversal intervals from [0,15] to [75,90] degrees; there is no universal 45-degree boundary.', '',
'## Negative, inconclusive, and limiting evidence', '',
'- The 45-degree structured-history contrast is inconclusive. All eight mean contrasts after isotropic training are inconclusive, not equivalent to zero.',
'- The uniform-direction reference after structured training is +0.0269 with interval [−0.0175, +0.0656]; it shows no resolved orientation preference. After isotropic training it is +0.0048 [−0.0407, +0.0536]. These finite references neither prove exact symmetry nor indicate a resolved violation.',
'- High predictor accuracy also occurs after isotropic training. It therefore supports this geometric predictor for the selected assay, not a claim that its usefulness uniquely requires structured history. No formal regime-level interaction was prespecified or tested.',
'- Ceiling effects are substantial: the organized arm exceeds 0.99 performance in 70.3% of 0-degree structured trials, and the rotated arm in 70.8% of 90-degree trials. The prespecified endpoint and horizon were retained. Separate arm means/ceiling rates and every trajectory are available; no alternative horizon was selected.',
'- Fixed-angle targets have only two identities (± the unit direction). Zero mismatch reuses structured-training target support. This is a controlled mismatch assay, not generalization to eight distinct unseen target identities.',
'- The model is two-dimensional, Gaussian, elitist, fixed-spectrum and noiseless in performance evaluation, with no mechanism-maintenance cost. A quarter-turn comparator preserves proposal spectrum/norm while deliberately changing orientation. Conclusions apply to that comparator and model.',
'- Ordinary historical selection can shape the retained orientation. This experiment does not establish selection specifically for future adaptability, general biological usefulness, or novelty relative to prior literature.', '',
'## Completion and files', '',
'The requested bounded exploratory experiment is complete. Independent recomputation from raw stored rows reproduced all 976 numerical summary fields within 1.05e-17, all classifications and all crossing records; no missing entries or hash inconsistencies were found. The independent reviewer did not rerun the simulation. A confirmatory or more realistic study would be a distinct prospective design; this result does not authorize seed expansion or threshold/horizon tuning to improve apparent success.', '',
'Authoritative HPC directory: `PRIVATE_HPC/organized-variation-transfer/experiments/mismatch_reversal_run_v1/`.', '',
'Key files: `result.json` (all histories and trajectories), `summary.json` (all contrasts and crossing records), `tests.log`, `ACCOUNTING.psv`, `runtime.json`, `SOURCE_SHA256SUMS`, `RESULT_SHA256SUMS`, `AUTHORIZATION.md`, `INDEPENDENT_RESULT_REVIEW.md`, and `mismatch_reversal.png`/`.svg`. Plot/report scripts only read stored results and never rerun the simulation.', '',
'Result SHA-256: `'+hashlib.sha256((ROOT/'result.json').read_bytes()).hexdigest()+'`.', '']
(ROOT/'REPORT.md').write_text('\n'.join(lines))
