# Supporting information: population state and organized variation

**Jack Chen**

Frederick Sequencing and Genomics Core; Advanced Biomedical Computational Science (ABCS); Frederick National Lab for Cancer Research; National Institutes of Health.

Research preprint, version 1.0, 22 September 2026. Computational study; not externally peer reviewed.

## S1. Evidence map and dependence

| Study | Question | Evidence and dependence |
|---|---|---|
| V1-V3 | Inherited versus rotated orientation across transfer directions | Same 48 historical inputs across three transfer settings; not three training replications. All V1-V3 per-trial result tables are included. |
| 002 | Earlier state by later rule | Four continuations from crossed generation-5 checkpoints on the original cohort. |
| 003 | Centroid and complete centered configuration | Eight-cell intervention on the same checkpoints; changes covariance and higher empirical structure together. |
| 004 | Prospective choices using M, G and E summaries | New 48-history cohort. Choices frozen before continuations; the 0.02 usefulness target was not attained. |
| 005 | Local calibration versus horizon change | New evaluation streams from a fixed panel of 004 checkpoints; no independent training replication. |

V1-V3 use 24 histories in each training regime, seven fixed transfer directions plus a uniform-direction reference, and eight paired trials per history/family. The two intervention stages reuse these histories. Study 004 supplies a second training cohort with the same group sizes. Study 005 selects trial IDs 0 and 1 prospectively, retaining both early states: 1,536 checkpoints, 24 conditional evaluation replicates each, with four branches sharing inputs within each paired row. There are 18,432 paired replicate rows, each retaining four branches; a row is not one independent historical replicate.

## S2. Statistical conventions

The unit for the reported population-level intervals is a whole historical training replicate. Transfer directions, trials, early arms and successive studies within a cohort remain dependent. Study 004 averages directions, trials and early arms equally within each history for its primary contrast, separately in each regime. No cohort pooling is used.

V1-V3 use the original bootstrap order statistics at sorted positions 50 and 1950 of 2,000 resamples. Later history grids use linearly interpolated percentile endpoints at 0.025 and 0.975. For early studies whose rows were not stored separately, publication packaging replays the original archived Python random seed and sampling order, stores those exact index rows, and verifies that they reproduce the original intervals. This adds no population observations and selects no new resampling seed. Studies 004 and 005 use their already stored regime-specific bootstrap rows. Small floating-point differences caused by arithmetic summation order are reported by the verifier.

Study 005's conditional sign classification uses two marginal 97.5% bootstrap intervals at each checkpoint, with a nominal Bonferroni joint 95% convention for those two horizons. This is approximate coverage and gives no simultaneous guarantee over the checkpoint panel. Counts of resolved reversals or contradictions describe this procedure, not known underlying error probabilities. The publication verifier recomputes history-level statistical grids; the prior internal reconstruction covers the conditional estimates from raw retained outputs. The large raw checkpoint/continuation archive is not included here.

## S3. Sign conventions and exact quantities

The transfer and state-intervention figures display O-minus-R performance, so a positive value favors the inherited orientation. The conditional calibration experiment instead uses O-minus-R loss, equivalently R-minus-O performance; a positive value favors the rotated rule. The figures label their conventions explicitly.

For conditional prediction a and replicate contrast D, subtracting the estimated variance of the replicate mean from (a minus mean D) squared gives an unbiased estimate of squared error against the conditional mean under independent replicates and finite second moments. The finite estimate can be negative. The local-error, horizon-change and signed cross-term estimates satisfy an algebraic identity but are not disjoint causal contributions. No component is floored at zero and no negative estimate is discarded.

The Gaussian formula in the manuscript is exact for ideal normalized weighting of a specified mixture. The actual process samples sequentially without replacement from a finite random candidate pool, retaining parents. An expectation of unnormalized offspring weight is neither a survival probability nor long-horizon expected population performance. These quantities must remain separate even when the formula is evaluated without numerical error.

## S4. Unfavorable and unresolved results

The geometry-aware starting-state predictor loses to the original predictor at the fixed terminal endpoint. Its descriptive early-horizon success does not move that endpoint. The fresh-cohort E-minus-M gain remains below 0.02, Gaussian moments achieve most of it, and switching is a strong baseline. The hindsight headroom calculation is post hoc and cannot be used as an operating policy or a general bound for other policy classes.

The structured 75-degree state comparison has the same positive point estimate under two bootstrap seeds but one interval includes zero. It is reported as uncertain. This does not reverse the supported state-by-rule interaction. Subgroup harms, unresolved three-factor results and negative corrected estimates remain in the complete statistical grids. No subgroup or seed was added to make these results positive.

## S5. Reproduction and data boundary

Run `python scripts/reproduce_statistics.py` to recompute the reported history-level means and intervals from included aggregates and stored index rows. Run `python scripts/rebuild_figures.py` to regenerate the six main figures and the transfer overview. Run `python scripts/verify_release.py` for file hashes, provenance, figure sources and local links. Install dependencies from `requirements.txt` first.

Archived model and analysis files are organized by study in `code/`; configuration and complete summary grids are in `results/`. These source files are supplied for inspection and may require omitted large input archives for execution. The package does not claim complete raw-trajectory reproduction. Scientific results are unchanged from the accepted studies. Publication preparation runs statistical reductions and plotting only.

The separate private-memory manuscript concerns inherited strategy transmission in a different binary model: [Zenodo record](https://doi.org/10.5281/zenodo.22907237). It is not independent replication of this two-dimensional transfer study. The companion memory-and-fresh-search preprint concerns an externally imposed shared-cache search policy, not variation-rule switching. Each paper discloses its own evidence scope.
