# V3: unequal fitness consequences and two fixed predictors

One user-authorized bounded exploratory execution under the current project authorization. Read EXTERNAL_V2_REVIEW.md (accepts v2 and identifies circular fitness geometry as a remaining assumption). Preserve v1/v2 and shared records. After results, assess the combined evidence and stop rather than automatically adding variants. No publication-readiness gate is required.

## Exact intervention and inputs

Reuse v2 result SHA256 `b595f14237a8375ffc9b942f1fbfe4ee71a8a4020214380b7863bc93a171cd0c`, all 48 inherited orientations and exact 3,072 target/trial entries, historical regime labels, population 32, SDs .12/.02, quarter-turn comparator, coefficient 10 and 25-generation horizon. No training. Use new master seed 2026092103 and domain-separated `v3-mutation`/`v3-survival` seeds, recorded per pair. Common Gaussian innovations and survival uniforms couple the arms without changing marginal probabilities; corresponding regimes share streams by historical index, family and trial as in v2. No parameter or seed tuning after outcomes.

H = R(30 degrees) diag(4,1) R(30 degrees)^T = [[13/4,3 sqrt(3)/4],[3 sqrt(3)/4,7/4]]. Let d=t^T Ht, A=H/d. Loss is L(x,t)=(x-t)^T A(x-t). At x=0 it equals 1, for all supplied targets. Each generation produces one child per parent and sequentially samples 32 of 64 distinct candidate indices without replacement, with remaining-candidate weights exp(-10 L). Performance is 1-mean(L). Scores may decrease and may be negative; only finiteness and the theoretical upper bound 1 (1e-12 roundoff allowance) are required. Unit Euclidean targets give the v2 loss when H=I; focused tests also compare entire identity-metric transfer trajectories under identical test random streams.

Covariance rotation preserves Euclidean eigenvalues, trace, determinant and paired proposal lengths. It does NOT preserve mutation consequences in the new metric: tr(H C), or tr(A C) at a target, generally changes. The contrast deliberately changes orientation relative to fitness curvature; it is not fitness-metric resource matching.

## Two predictions, fixed without population outcomes

1. Original predictor: use the exact v2 stored directional-variance value, `(major_sd^2-minor_sd^2)*cos(2*(orientation-target direction))`.
2. Geometry-aware predictor: log expected *offspring survival weight* at x=0 for organized covariance minus that for the quarter-turned covariance. A survival weight is not a survival probability in the finite competition pool.

Derivation: for offspring displacement delta=Bz, z~N(0,I), C=BB^T, write

`-beta L(delta,t) - z^T z/2 = -beta t^T A t - z^T K z/2 + b^T z`,

where `K=I+2 beta B^T A B` and `b=2 beta B^T A t`. Completing the square and integrating the normalized Gaussian gives

`log E[exp(-beta L(delta,t))] = -beta t^T A t - 1/2 log det K + 1/2 b^T K^-1 b`.

Here `t^T A t=1`, beta=10. The implementation uses a 2×2 Cholesky factor of K and its triangular solve, avoiding inverse covariance and the nonsymmetric product C A. This expression is invariant to the chosen square root of C. It handles the zero-covariance limit and is cross-checked against an independent diagonal formula and deterministic numerical quadrature. No fitting or empirical prediction calibration.

Both prediction panels, individual log expectations, signs, seeds and inputs are written and hashed as `predictions.json` before any scientific transfer is started. Frozen predictions are checked after transfer. Unit-test toy trajectories establish correctness only; they do not choose parameters. The second statistic is explicitly LOCAL: it is not a theorem about 25-generation selected-population performance, which also depends on state change, competition, order statistics and stochastic survival.

## Prespecified complete analysis

Retain all 48 historical inputs, 3,072 pairs, both arms and all 25 trajectory pairs. Report all 16 family/regime population contrasts, both arm means, per-arm negative endpoints/transient values, declines and >.99 ceiling fractions. Group eight trials within each history; equally weight 24 historical units per regime. Use 2,000 whole-history bootstrap resamples, fixed `bootstrap` seed namespace, percentile pointwise 95% intervals. Classify positive/negative means by interval endpoints, otherwise inconclusive. No multiplicity correction, equivalence margin or confirmation claim.

For BOTH predictors: average the per-trial statistic within each history/family, compare its sign with the mean population delta, report signs/values/errors for every history, and aggregate seven-angle grid accuracy per regime. Use 1e-12 tie tolerance and .5 credit if either sign is tied; otherwise exact sign agreement gives 1, error 0. Retain uniform-direction reference results separately. Report both always-benefit and always-harm baselines. Paired geometry-minus-original accuracy is first averaged across seven angles WITHIN each history; report its mean and exploratory pointwise 95% history-bootstrap interval using `paired-predictor-accuracy` namespace and 2,000 resamples. This is not 168 independent validation units. No post-outcome choice between denominators or ties.

Crossings: report ALL directions, positive-to-negative AND negative-to-positive, along the fixed 0–90-degree grid. Join consecutive non-tied entries with opposite signs; preserve intervening ties. Retain every predicted and observed crossing list, empty lists, multiple crossings, all tie points and full grid signs for each of 48 historical inputs. Compare each predictor's entire crossing list with the observed list using fixed categories: ties_present; neither_detected; observed_only; predicted_only; same_crossings; different_crossings. A multiple list can match exactly; its multiplicity remains explicit. No unique crossing, zero near 45 degrees, or crossing outside the sampled range is assumed. Grid brackets are descriptive, not confidence intervals for a true root.

V2 arm means/deltas may be shown as context, with an explicit warning that different metrics are different endpoints: a v2-to-v3 numerical change is not a common-loss improvement estimate. Target normalization keeps start loss 1 but does not equalize later difficulty across families. Reusing historical inputs is not independent replication of training or a test of probabilistic/anisotropic training.

## Correctness, execution and stopping

Tests cover H entries/eigenvalue ratio, normalized initial loss, identity-metric recovery, whole-trajectory recovery under H=I, metric-scale invariance, diagonal and zero-covariance Gaussian oracles, independent 2-D Simpson quadrature, joint rotation of coordinates/H, Euclidean-versus-metric resources, unchanged sequential sampling, negative-tolerant validation, predictor freeze without outcome/training access, both crossing directions/multiplicity/ties/missing lists, and frozen configuration/panel.

One norm request, one CPU, 2 GiB requested memory, 15-minute Slurm ceiling, 780-second application timeout, no automatic requeue. Tests must pass before the full scientific panel. Record source/input hashes, runtime, prediction freeze, test logs, all scientific outputs and terminal accounting. Do not alter sources or restart a failed scientific attempt without a new explicit decision. Stop after this experiment's outputs, integrity checks and combined-results assessment; no automatic next variant.
