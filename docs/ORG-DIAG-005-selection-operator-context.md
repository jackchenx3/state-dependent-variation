# Interpreting the local selection approximation

Prepared while ORG-DIAG-005 runs. This note changes no assignment, prediction or scientific input. It supplies mathematical context for interpreting the completed diagnostic, not a new simulated result.

## Established sampling distinction

Sequential weighted draws without replacement make each remaining item's weight determine its probability at the next draw. The final inclusion probabilities are generally not proportional to the original weights. Efraimidis explicitly separates these sampling definitions and gives a four-item example. [Efraimidis, *Weighted Random Sampling over Data Streams*, definitions 1–3 and example 1](https://arxiv.org/pdf/1012.0256).

Using that example scaled to weights (1,1/2,1/2,1/2), draw two distinct items. The weight-1 item has inclusion probability `1/(5/2) + [3(1/2)/(5/2)] [1/2] = 7/10`. Each other item has inclusion probability 13/30. The expected fraction of selected items with the heavier weight is therefore 7/20, while simple normalized weighting assigns it mass 2/5.

For losses 0 and log(2)/beta, these weights equal exp(−beta loss). Expected mean loss is `(13/20) log(2)/beta` under sequential sampling, versus `(3/5) log(2)/beta` under normalized weighting: a difference of `log(2)/(20 beta)`. This is an adaptation of the established example, not an algorithmic discovery.

## Implication for the current project

The implemented transfer sampler retains N of 2N parent/offspring candidates using sequential weighted draws without replacement. The policy's Gaussian functional instead describes ideal normalized weighting of a parent/offspring distribution. Exact Gaussian integration does not make those two operations identical. The example establishes a possible loss-calibration discrepancy, not an O-versus-R ranking error or its magnitude in our experiment.

There is also a distinct random-pool issue. Even a replacement sampler applied to a realized finite candidate pool would involve its realized ratio of weighted loss to total weight. Averaging that ratio over random offspring does not generally equal dividing the expected numerator by the expected denominator. Our ideal mixture uses the latter distribution-level normalization. These distinctions can coexist; the current diagnostic does not isolate their separate contributions or test a large-N limit.

For a realized pool, the actual expected selected mean loss can be written as `(1/N) sum_i pi_i(pool) L_i`, where pi_i is that candidate's inclusion probability under the implemented sampler. The process expectation then averages this quantity over new offspring pools. This clarifies why “the local formula is exact” and “the local formula predicts this sampler's mean” are separate statements.

## How to read ORG-DIAG-005

- A resolved positive Monte Carlo-corrected squared contrast error at generation 6 supports a discrepancy between the frozen local prediction and the conditional expected contrast of the actual process on this panel. It does not diagnose a coding bug by itself.
- A resolved expected-contrast sign change between generations 6 and 25 supports a horizon ranking change, separately from local calibration error.
- The two discrepancies may overlap, reinforce or partly cancel. The prespecified cross term and unresolved cases must remain visible. Neither the counterexample nor a positive squared error alone establishes a ranking error for a particular checkpoint.
- Do not relabel every discrepancy finite-population noise, uniquely apportion all failures, fit a replacement policy, or change the current design on the basis of this note.

The completed diagnostic should determine the next research decision. Historical memory versus recency and broader model generality remain distinct approaches in the ledger; this literature clarification is not authorization for an indefinite sequence of revised local predictors.
