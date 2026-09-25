# Study 064: a small contribution from configuration beyond initial moments

Accepted after separate supervisor reconstruction. This is a finite-population simulation result, not an exact theorem about population performance. The initial matching identity is mathematical; its finite implementation was checked separately.

The fixed negative prediction was supported: on structured histories, native-minus-reshaped state-by-rule interaction was -0.740782 [-1.015989, -0.448922] percentage points. The original interaction remained large: -32.720150 [-34.580356, -30.990435] points natively and -31.979368 [-33.831282, -30.243071] after reshaping. Thus the intervention modestly attenuated, rather than removed, the interaction.

All first two trait moments and initial quadratic mean loss were preserved within the fixed tolerance. This supports a contribution from empirical configuration beyond those initial summaries under the specified intervention. It does not isolate a unique higher moment, show that higher structure explains most of the original interaction, or establish a new useful policy.

## Fixed pooled comparisons

Intervals below are approximate pointwise exploratory 95% whole-history bootstrap intervals. All quantities are percentage points.

| Quantity | Structured | Isotropic | Structured minus isotropic |
|---|---:|---:|---:|
| J_NATIVE | -32.720150 [-34.580356, -30.990435] | -33.833290 [-35.923423, -31.833441] | +1.113140 [-0.999708, +3.134421] |
| J_SHAPE | -31.979368 [-33.831282, -30.243071] | -33.534208 [-35.708612, -31.516643] | +1.554840 [-0.428272, +3.506337] |
| DELTA | -0.740782 [-1.015989, -0.448922] | -0.299083 [-0.666843, +0.050407] | -0.441700 [-0.974416, +0.086306] |
| G_MEAN | +0.243637 [+0.176620, +0.311369] | +0.287749 [+0.200407, +0.372488] | -0.044113 [-0.148395, +0.055879] |

The isotropic primary analogue and the direct regime difference remain unresolved. A resolved structured result beside an unresolved isotropic result does not establish a regime difference. Native configurations had a small positive average-performance advantage over reshaped ones in both regimes; G_MEAN is a separate companion outcome, not the primary interaction.

## Conditional and contrary evidence

Structured family DELTA intervals were negative at 15, 30, 45 and 90 degrees, and unresolved at 0, 60 and 75 degrees and in the uniform-direction family. Every isotropic-history family was unresolved except its uniform-direction family, which was negative. These pointwise comparisons do not have simultaneous coverage. The complete 380-record grid is retained without selecting favorable families.

Three of 24 structured history-block DELTA means had the opposite sign. All observed declines were retained. No negative performance values occurred in the retained generation-5 to generation-25 panel; this does not alter earlier studies with negative values. Initial matching did not persist dynamically: centroid and covariance subsequently diverged.

## Execution and independent checks

Job 53356937 completed in 193 seconds using one CPU, with 4 GiB requested and batch MaxRSS 167,532 KiB. Exactly 12,288 new continuations were compared with 12,288 stored native controls. All 48 historical inputs and 3,072 paired rows remained. No training or native control was replayed. All 248 delivery files were verified locally and on HPC.

The supervisor separately reconstructed all 380 estimates, 6,144 initial state matches, 64 fixed sampler matrices and the preselected history-0 block: 512 paths, 10,240 updates and 655,360 candidate scores. No producer implementation was imported. Maximum interval discrepancy was 4.44e-16. The local/HPC sampler comparison differed by at most 3.00e-15 and reconstructed selected coordinates by 4.44e-16, both within the frozen 1e-12 tolerance; all survivor indices matched exactly. These are floating arithmetic differences, not new states selected by a different index order. No audit expansion or scientific rerun was required.

## Scientific decision and next deliverable

Integrate this result into the existing state-dependent-variation manuscript. Its discussion explicitly deferred separation of covariance from higher empirical configuration; this intervention changes that narrow decision. The small scale and persistent large interaction prevent a stronger mechanism claim. A coherent version update is warranted; a separate paper is not warranted by this study alone.

The next finite deliverable is MANUSCRIPT-STATE-SHAPE-064: a v1.1 draft of that paper and supplement, authenticated compact 064 exports, two source-bound figures, and 380 added estimate checks alongside 7,940 preserved estimates. This is not an addition to the distinct binary private-memory paper. No new numerical variant is active.

Reused original histories, reused continuation randomness, one fixed row-space sampler, the generation-25 horizon, initial-only matching and abstract reachability remain limitations. The mathematical Gaussian formula in the previous paper is neither contradicted nor shown sufficient for this finite empirical population. Broader biological and future-guidance conclusions remain outside the evidence.
