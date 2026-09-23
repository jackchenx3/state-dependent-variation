"""Present complete fixed v1/v2 outcomes; read-only scientific inputs."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
v1=json.loads((P/'baseline_result.json').read_text());v2=json.loads((P/'result.json').read_text())
c=json.loads((P/'comparison.json').read_text());audit=json.loads((P/'AUDIT.json').read_text())
def interval(values):return '[{:+.4f}, {:+.4f}]'.format(*values)
def bracket(record):
    crosses=record['crossings']
    return '; '.join('['+', '.join(x['bracket'])+']'+(' (ties)' if x['tie_points'] else '') for x in crosses) if crosses else 'none'
L=['# V2: probabilistic survival preserves the sampled benefit-to-harm pattern', '',
'**The v1 reversal does not require guaranteed survival of the best candidates in this specified transfer assay.** With sequential survival without replacement and weights exp(−10 × squared distance), the structured-history mean contrast remains positive at sampled mismatches 0°, 15°, 30°, unresolved at 45°, and negative at 60°, 75°, 90°. Predictor accuracy remains high but is not perfect. This is a conditional exploratory comparison using the same stored histories, not independent training replication.', '',
'## Executed experiment', '',
'- **Job 53276437: COMPLETED, exit 0:0**, cn123, 75 seconds elapsed, 75.002 parent CPU seconds. One CPU, 2 GiB requested memory, batch MaxRSS 56,352 KiB (about 55.0 MiB). `norm` was requested; accounting records `short`. The job stayed within the authorized 15-minute ceiling.',
'- **14 correctness tests passed before scientific transfer.** Exactly 48 reused historical orientations and 3,072 paired trajectories were analyzed. No failed/excluded histories, replacement seeds, extra scientific run, or post-outcome tuning.',
'- Exactly the stored v1 angles and targets were reused. Mutation spectrum, population 32, quarter-turn comparator, zero transfer starts and generation-25 endpoint were unchanged. Survival samples 32 distinct candidate indices from 64 sequentially; coefficient 10 is fixed and exploratory, not biologically calibrated.',
'- Fresh master seed **2026092102** and separate recorded mutation/survival seeds appear in every result row. Both arms share random innovations/uniforms while using their own survival weights. v1 was not rerun with these streams.',
'- '+str(audit['checks'])+' stored-output arithmetic/integrity checks passed, including source/result hashes, exact historical inputs/predictors, all contrasts and bootstrap intervals, paired-change intervals, failure roster, declines and negative scores. This audit did not import or execute the model.', '',
'## Full mean contrasts and unresolved effects', '',
'Delta is organized minus rotated normalized squared-distance improvement. Intervals are the fixed **pointwise exploratory 95% whole-history bootstrap intervals**, 2,000 resamples, 24 stored history units per regime. They are not simultaneous or multiplicity-adjusted. Confidence concerns the conditional history/transfer panel; no new training histories were generated. Values are reported without excluding predictor misses.', '',
'| Stored training regime | Family | V1 delta [95% interval] | V2 delta [95% interval] | V2 classification |',
'|---|---:|---|---|---|']
for x in c['contrasts']:
    a,b=x['v1'],x['v2']
    L.append('| {} | {} | {:+.4f} {} | {:+.4f} {} | {} |'.format(x['regime'],x['family'],a['mean_delta'],interval(a['exploratory_pointwise_95_interval']),b['mean_delta'],interval(b['exploratory_pointwise_95_interval']),b['classification']))
L+=['',
'The 45° structured comparison, the structured uniform-direction reference, and all eight isotropic-history mean comparisons remain inconclusive. Intervals crossing zero do not establish equivalence. The sampled grid and history-specific bracket variability do not identify a universal or exact 45° reversal.', '',
'## Both arms and the paired rule comparison', '',
'Each score is `1 − mean squared target distance / initial squared target distance`. A negative score is worse than the initial population, and a negative delta is worse than the rotated comparator; these are different meanings of harm. Both arm means at generation 25 are lower in v2 than v1 in every family/regime. Thus the larger structured contrast magnitudes do not mean that probabilistic survival improves absolute adaptation.', '',
'Paired change is `(v2 organized − v2 rotated) − (v1 organized − v1 rotated)`, averaged over matched historical inputs. Bootstrap resamples matched history indices. It includes fresh transfer Monte Carlo variability and is not a matched-random-number replay of v1.', '',
'| Regime | Family | V1 organized | V1 rotated | V2 organized | V2 rotated | Paired delta change [95% interval] |',
'|---|---:|---:|---:|---:|---:|---|']
for x in c['contrasts']:
    a,b=x['v1'],x['v2']
    L.append('| {} | {} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:+.4f} {} |'.format(x['regime'],x['family'],a['mean_organized'],a['mean_rotated'],b['mean_organized'],b['mean_rotated'],x['paired_delta_change'],interval(x['paired_change_pointwise_95_interval'])))
L+=['',
'The pointwise paired intervals indicate increased positive contrast at structured 0°, 15°, 30° and more negative contrast at 60°, 75°, 90°. The structured 45° and uniform-direction changes and all isotropic-history changes are unresolved. This is an exploratory rule comparison, not a claim of practical importance or general superiority of either process.', '',
'## Predictor accuracy and every failure', '',
'The preexisting directional-variance predictor is unchanged. Its labels use the inherited orientation and known target direction, not the observed transfer scores. Accuracy counts angles within each history as correlated observations; 168 comparisons are not 168 independent replicates.', '',
'| Stored regime | Version | Correct grid signs / 168 | Sign accuracy | Always benefit | Always harm | Same reversal bracket / 24 |',
'|---|---|---:|---:|---:|---:|---:|']
for reg,versions in c['grid_accuracy'].items():
    for ver,x in versions.items():
        L.append('| {} | {} | {:.0f} | {:.2%} | {:.2%} | {:.2%} | {} |'.format(reg,ver,x['weighted_sign_matches'],x['sign_accuracy'],x['always_benefit_accuracy'],x['always_harm_accuracy'],x['localization']['counts']['same_bracket']))
L+=['',
'V2 structured localization: 22 same brackets, one different bracket and one predicted-only crossing. V1 had 22 same and two different. The unchanged total therefore hides changed failure identities. V2 isotropic localization: 11 same, four different and nine with neither positive-to-negative crossing; v1 had 15 same and nine neither. “Neither” is not a successfully localized reversal. No accuracy confidence interval or formal accuracy-equivalence claim is supplied.', '',
'All v2 predictor sign failures, including the uniform-direction reference (zero-based history IDs):', '',
'| Regime | Family | History | Predictor | V1 observed delta | V2 observed delta |',
'|---|---:|---:|---:|---:|---:|']
for x in c['predictor_failures_and_ties']:
    L.append('| {} | {} | {} | {:+.8f} | {:+.6f} | {:+.6f} |'.format(x['regime'],x['family'],x['history'],x['predictor'],x['v1_delta'],x['v2_delta']))
L+=['',
'All unresolved/mismatched v2 positive-to-negative localization cases, excluding the separately reported nine “neither” cases:', '',
'| Regime | History | Predicted bracket | Observed v1 | Observed v2 | V2 category |',
'|---|---:|---|---|---|---|']
for x in c['bracket_comparison']:
    a,b=x['v1'],x['v2']
    if b['agreement'] not in ('same_bracket','neither'):
        L.append('| {} | {} | {} | {} | {} | {} |'.format(x['regime'],x['history'],bracket(b['predicted']),bracket(a['observed']),bracket(b['observed']),b['agreement']))
L+=['',
'All 48 full crossing records, including missing/tied/multiple cases, are retained in comparison.json and summary.json. No failure was relabeled as a tie, dropped, or used to tune the coefficient, seed or horizon.', '',
'## Valid declines and negative performance', '',
'Probabilistic survival correctly removes the monotonicity guarantee. Validators require finite values and the mathematical upper bound of 1; they deliberately do not require nonnegative or nondecreasing improvement.', '',
'| Version | Arm | Trials | Any declining generation | Declining transitions / 76,800 | Any negative score | Negative endpoints | Minimum recorded score |',
'|---|---|---:|---:|---:|---:|---:|---:|']
for version,data in [('v1',v1),('v2',v2)]:
    for arm,i in [('organized',0),('rotated',1)]:
        ds=[x[version+'_diagnostics'][arm] for x in c['contrasts']]
        L.append('| {} | {} | {} | {} | {} | {} | {} | {:.6f} |'.format(version,arm,sum(x['trials'] for x in ds),sum(x['trials_with_decline'] for x in ds),sum(x['declining_transitions'] for x in ds),sum(x['trials_with_negative_score'] for x in ds),sum(x['negative_endpoints'] for x in ds),min(p[i] for row in data['rows'] for p in row['trajectory'])))
L+=['',
'Negative values occur during v2 trajectories, while all generation-25 endpoints in this run are positive. These transient setbacks were preserved as scientific outcomes, not classified as test failures. Arm-specific ceiling fractions at >0.99 are reported for every family in both version summaries and comparison.json.', '',
'## Scope and interpretation', '',
'- The observed reversal persists after replacing guaranteed elitist retention with the specified probabilistic survival rule. This tests one dependence of the transfer assay; it does not establish robustness to every turnover/reproduction mechanism or coefficient.',
'- These are exactly v1’s historical inputs. The experiment says nothing about whether probabilistic **training** would produce these orientations, and provides no independent replication of training or a new causal history-acquisition comparison.',
'- Both rules retain the reflection/bisector and quarter-turn geometry described in the external review: weights depend only on squared distance. High predictor accuracy remains partly constrained by that geometry; it does not establish unknown-future prediction, a unique crossing, or biological generality.',
'- Coefficient 10 is a fixed exploratory design choice. The original spectrum, target radius, two-dimensional phenotype, noiseless score, frozen inherited orientation and fixed horizon remain strong assumptions.',
'- Fixed-angle families contain only two target identities, and zero mismatch reuses the structured historical support. This does not demonstrate generalization to unseen identities.',
'- All mean classifications and rule-change intervals are pointwise and exploratory; accuracy/localization are descriptive. No effect margin, multiplicity-controlled confirmation, equivalence claim, or post-outcome horizon selection is introduced.', '',
'## Deliverables and preservation', '',
'Authoritative HPC directory: `PRIVATE_HPC/organized-variation-transfer/experiments/mismatch_reversal_run_v2/`.', '',
'Source/configuration: model.py, baseline_model.py, comparison.py, execute.py, test_model.py, config.json, PROTOCOL.md, job.sbatch, SOURCE_SHA256SUMS. Evidence: tests.log, runtime.json, ACCOUNTING.psv, COMPLETION.json, FINAL_STATUS.json, RESULT_SHA256SUMS, AUDIT.json and audit_outputs.py. Complete outcomes: result.json, summary.json, comparison.json. Plots: v1_v2_performance.png/.svg and v1_v2_prediction.png/.svg; plot_comparison.py reproduces them from stored data.', '',
'V1 and prior shared/historical records remain unchanged; the separate PRESERVATION.log records verification. No further scientific run was launched. This completes the authorized v2 execution milestone.', '',
'V2 result SHA-256: `'+hashlib.sha256((P/'result.json').read_bytes()).hexdigest()+'`.', '']
(P/'REPORT.md').write_text('\n'.join(L))
