"""Render complete stored evidence; no model calls, fitting or simulation."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
r=json.loads((P/'result.json').read_text());s=r['summary'];audit=json.loads((P/'AUDIT.json').read_text())
labels={'predictor':'Original','geometry_predictor':'Geometry-aware'}
def ci(v):return '[{:+.4f}, {:+.4f}]'.format(*v)
def crossings(x):
    out=[]
    for c in x['crossings']:
        direction='+ to −' if c['direction']=='positive_to_negative' else '− to +'
        out.append('{} [{}]{}'.format(direction,', '.join(c['bracket']),' ties='+','.join(c['tie_points']) if c['tie_points'] else ''))
    return '; '.join(out) if out else 'none detected'
errors=['# All v3 history-level predictor errors and ties','',
'Eight target/noise trials are averaged within each history/family. No case is excluded. Trial-level signs/errors are also retained in result.json; all history-level signs, including correct predictions, are in summary.json. IDs are zero-based.','',
'| Regime | Family | History | Predictor | Predicted value | Predicted sign | Observed mean delta | Observed sign | Credit |',
'|---|---:|---:|---|---:|---:|---:|---:|---:|']
for e in s['errors_and_ties']:
    errors.append('| {} | {} | {} | {} | {:+.9f} | {} | {:+.9f} | {} | {} |'.format(e['regime'],e['family'],e['history'],labels[e['predictor']],e['predicted_value'],e['predicted_sign'],e['observed_delta'],e['observed_sign'],e['credit']))
(P/'PREDICTOR_ERRORS.md').write_text('\n'.join(errors)+'\n')
cs=['# Every v3 observed and predicted crossing','',
'All 48 histories are retained. These are finite-grid sign-change brackets, not exact roots or confidence intervals. Both directions are reported. “None detected” is not evidence that the underlying expectation has no root outside or between sampled points. No multiple or tied crossing was observed in this run, but the implementation and records support them.','',
'| Regime | History | Observed | Original prediction | Geometry-aware prediction | Original agreement | Geometry-aware agreement |',
'|---|---:|---|---|---|---|---|']
for x in s['all_crossings']:
    cs.append('| {} | {} | {} | {} | {} | {} | {} |'.format(x['regime'],x['history'],crossings(x['observed']),crossings(x['predicted']['predictor']),crossings(x['predicted']['geometry_predictor']),x['agreement']['predictor'],x['agreement']['geometry_predictor']))
(P/'ALL_CROSSINGS.md').write_text('\n'.join(cs)+'\n')
L=['# V3: unequal fitness consequences reveal a local-predictor failure','',
'**The original predictor remains descriptively accurate for signs, but its crossing localization is imperfect. The proposed geometry-aware local statistic performs worse.** With the specified anisotropic loss, original grid accuracy is 155/168 (92.26%) for structured historical inputs and 162/168 (96.43%) for isotropic inputs; geometry-aware accuracy is 144/168 (85.71%) in each group. This negative result is retained without tuning or rerunning.','',
'The population contrast is still beneficial at structured target angles 0°, 15°, 30° and harmful relative to the rotated control at 75°, 90°. Both 45° and 60° are unresolved. All isotropic-input mean contrasts and both uniform-direction references are unresolved. No unique reversal or boundary near 45° is inferred.','',
'## Completed execution and fixed prediction','',
'- **Slurm job 53276643: COMPLETED, exit 0:0**, cn131, 78 seconds elapsed, 76.126 parent CPU seconds. One CPU, 2 GiB requested memory, batch MaxRSS 66,128 KiB (about 64.6 MiB). `norm` was requested; accounting records `short`. The 15-minute ceiling was respected.',
'- **13 tests passed before scientific transfer**, including identity-loss and trajectory recovery for H=I, diagonal/zero-covariance analytic checks, independent 2-D Gaussian quadrature, coordinate/H rotation, sampling, negative scores, and all crossing directions.',
'- Exactly **48 reused historical orientations** and **3,072 paired trajectories**, no new training, exclusions or additional scientific run. The target panel, population, mutation spectrum, quarter-turn comparator, coefficient 10 and generation-25 endpoint match v2. Master seed 2026092103 supplies fresh recorded mutation/survival streams.',
'- Every predictor value, both individual log expectations, signs, target, orientation and seed was written in predictions.json and hashed in PREDICTION_FREEZE.json **before scientific transfer started**. Recorded ordering and frozen values match result provenance.',
'- Separate stored-output audit: **'+str(audit['checks'])+' checks passed**, with no experiment imports or simulation. An alternate covariance-precision formula reproduced all log expectations with maximum discrepancy '+format(audit['max_independent_log_expectation_error'],'.3g')+'. All contrasts/intervals, paired accuracy intervals, sign failures, crossings, declines and negatives reproduce.','',
'## Geometry and predictor meaning','',
'Use H = R(30°) diag(4,1) R(30°)ᵀ, A = H/(tᵀHt), L=(x−t)ᵀA(x−t), survival weight exp(−10L), and performance 1−mean(L). All populations start at loss 1. Negative improvement remains valid. Covariance rotation preserves **Euclidean mutation resources**, not fitness-metric consequences: tr(HC), and target-normalized tr(AC), generally differ between arms.','',
'For offspring δ=Bz from the common starting state, z~N(0,I), β=10, K=I+2βBᵀAB and b=2βBᵀAt:', '',
'`log E[exp(−βL(δ,t))] = −β − ½ log det K + ½ bᵀK⁻¹b`.', '',
'The geometry-aware predictor subtracts the rotated-arm log expectation from the organized-arm log expectation. This is an analytic **local offspring weight statistic**, not a survival probability in a competing pool and not a theorem about selected-population performance 25 generations later. The original predictor is exactly v2’s directional-variance statistic. Neither was fitted to v3 outcomes. The full derivation and prospective rules are in PROTOCOL.md.','',
'## Every population contrast and both arms','',
'Each of the 24 historical inputs per regime contributes its mean over eight trials. Intervals are predeclared pointwise exploratory 95% whole-history bootstrap intervals (2,000 resamples); no multiplicity correction or equivalence margin. “Harm” below means lower performance than the rotated comparator, not necessarily a negative absolute endpoint.','',
'| Historical regime | Target family | Organized mean | Rotated mean | Delta | Pointwise 95% interval | Classification | Original accuracy | Geometry accuracy |',
'|---|---:|---:|---:|---:|---|---|---:|---:|']
for c in s['contrasts']:
    L.append('| {} | {} | {:.4f} | {:.4f} | {:+.4f} | {} | {} | {:.2%} | {:.2%} |'.format(c['regime'],c['family'],c['organized']['mean'],c['rotated']['mean'],c['mean_delta'],ci(c['pointwise_95_interval']),c['classification'],c['sign_accuracy']['predictor'],c['sign_accuracy']['geometry_predictor']))
L+=['',
'Only sampled target directions are assessed. The mean curve changes sign between 45° and 60°, but both intervals cross zero; this is not a precise estimate of a population boundary. Normalizing starting loss does not make later difficulty identical across directions. V2 and v3 use different fitness metrics, so their numerical endpoint means must not be read as improvement on a common objective. V2 values are retained as context in summary.json.','',
'## Paired predictor comparison and errors','',
'| Historical inputs | Original signs | Geometry-aware signs | Geometry − original accuracy | Pointwise 95% history-bootstrap interval |',
'|---|---:|---:|---:|---|']
for reg,entries in s['grid_accuracy'].items():
    a=entries['predictor'];b=entries['geometry_predictor'];d=entries['geometry_minus_original']
    L.append('| {} | {:.0f}/{} | {:.0f}/{} | {:+.2f} percentage points | [{:+.2f}, {:+.2f}] percentage points |'.format(reg,a['weighted_matches'],a['comparisons'],b['weighted_matches'],b['comparisons'],100*d['mean'],100*d['exploratory_pointwise_95_interval'][0],100*d['exploratory_pointwise_95_interval'][1]))
L+=['',
'Accuracy differences are paired within history, averaging its seven angles before resampling. The 168 comparisons per regime are correlated, not 168 independent validation units. These intervals support an exploratory shortfall of this particular local statistic, not failure of every possible geometry-aware predictor.','',
'Across all eight families, there are **20 original-predictor errors** and **57 geometry-aware errors** among 384 history-family comparisons; all are listed in PREDICTOR_ERRORS.md. Original errors comprise 13 structured-grid, six isotropic-grid, and one isotropic uniform-direction case. Geometry-aware errors comprise 24 per grid plus seven structured and two isotropic uniform-direction cases. No ties were used to hide failures.','',
'One clear failure is structured history 0 at 75°: the geometry-aware log-weight difference is **+0.802429**, while the mean generation-25 population contrast is **−0.147786**. This is not merely a rounding-level sign discrepancy. The analytic local expectation and the finite-horizon population result answer different questions. The present experiment does not isolate which later dynamical mechanism causes each disagreement.','',
'## Every observed, predicted and missing crossing','',
'All 48 complete crossing lists are in ALL_CROSSINGS.md and summary.json, with both positive-to-negative and negative-to-positive transitions, missing lists, full grid signs and tie locations.','',
'| Historical inputs | Observed +→− | Observed −→+ | No observed crossing | Multiple observed crossings |',
'|---|---:|---:|---:|---:|']
for reg in ('structured','isotropic'):
    rows=[x for x in s['all_crossings'] if x['regime']==reg]
    L.append('| {} | {} | {} | {} | {} |'.format(reg,sum(c['direction']=='positive_to_negative' for x in rows for c in x['observed']['crossings']),sum(c['direction']=='negative_to_positive' for x in rows for c in x['observed']['crossings']),sum(not x['observed']['crossings'] for x in rows),sum(len(x['observed']['crossings'])>1 for x in rows)))
L+=['','| Historical inputs | Predictor | Same nonempty crossing list | Different lists | Both missing | Observed only | Predicted only | Ties present |','|---|---|---:|---:|---:|---:|---:|---:|']
for reg,entries in s['grid_accuracy'].items():
    for p in ('predictor','geometry_predictor'):
        c=entries[p]['crossing_counts']
        L.append('| {} | {} | {} | {} | {} | {} | {} | {} |'.format(reg,labels[p],*(c[k] for k in ('same_crossings','different_crossings','neither_detected','observed_only','predicted_only','ties_present'))))
L+=['',
'Geometry-aware prediction misses an observed crossing entirely in six structured and twelve isotropic histories. Its two “both missing” cases per regime are not successful localization of a root. No multiple crossings happened to be detected on this grid, but none were excluded by the analysis. Compared with v1/v2 reports, v3 prospectively counts **both crossing directions**; old positive-to-negative-only bracket totals are not interchangeable with these totals.','',
'## Declines, negative scores and ceiling behavior','',
'| Arm | Trajectories | At least one decline | Declining transitions / 76,800 | At least one negative score | Negative endpoints | Minimum recorded improvement |','|---|---:|---:|---:|---:|---:|---:|']
for arm,i in [('organized',0),('rotated',1)]:
    vals=[c[arm] for c in s['contrasts']]
    L.append('| {} | {} | {} | {} | {} | {} | {:.6f} |'.format(arm,sum(c['trials'] for c in vals),sum(c['trajectories_with_decline'] for c in vals),sum(c['declining_transitions'] for c in vals),sum(c['negative_any'] for c in vals),sum(c['negative_endpoints'] for c in vals),min(p[i] for row in r['rows'] for p in row['trajectory'])))
L+=['',
'All negative/transient declines are retained. Every final endpoint in this run is positive; that was not imposed by the validator. Separate >0.99 arm ceiling fractions for every family are in summary.json. The horizon was not changed after seeing predictor errors.','',
'## Combined assessment and stopping decision','',
'COMBINED_ASSESSMENT.md integrates v1–v3. In brief: the sampled conditional orientation effect survives one change in survival and one specified anisotropic metric; the original predictor is not exact; and analytically correct local weight expectations can be worse predictors of longer-horizon population ranking. These are model-specific findings using reused, elitistically trained orientations. They do not establish probabilistic training, new-history replication, new-target generalization, biological calibration or general foresight.','',
'**Stop here. No further variant or automatic rerun is being launched.** The combined evidence should be assessed on its own terms before a separately authorized next question. Publication readiness was not a condition of this run.','',
'Authoritative HPC directory: `PRIVATE_HPC/organized-variation-transfer/experiments/mismatch_reversal_run_v3/`. Source/config/tests, complete raw outcomes, prediction freeze, summary, audits, scheduler records and PNG/SVG figures are preserved there. V1/v2 and shared historical records are unchanged; see PRESERVATION.log.','',
'V3 result SHA-256: `'+hashlib.sha256((P/'result.json').read_bytes()).hexdigest()+'`.', '']
(P/'REPORT.md').write_text('\n'.join(L))
