# ORG-STATE-SHAPE-064 — empirical population shape at matched centroid and covariance

Revision 1. Sole finite execution assignment under continuing user authorization. Freeze and acknowledge this specification's SHA-256 before implementation/production. The design fixtures and source authentication passed before any new scientific checkpoint transformation or continuation outcome. Preserve prior studies, publications and original handoffs.

## Question, prediction and limits

Does the finite population's arrangement beyond its centroid and full trait covariance contribute to the previously observed early-state-by-later-rule interaction? Study003transferred complete centered configurations, while011–013tested proposal laws. This experiment instead reshapes the **trait population**, preserving its initial first two moments and quadratic mean loss, then uses the unchanged homogeneous later rules and selection operator.

The sole primary is `structured|ALL8|DELTA` at generation25. DELTA is the original early-state-by-rule interaction minus the corresponding interaction after moment-preserving reshaping. The working prediction is **negative**, meaning the original negative interaction is attenuated by reshaping. A resolved positive DELTA contradicts that directional prediction but still shows an effect of the specified beyond-moment intervention. An interval including zero is unresolved, not evidence that first two moments are sufficient. Retain every signed conditional result; do not substitute another primary after outcomes.

This is a mechanistic intervention on an abstract finite population. No practical-benefit threshold, unique fourth-moment mediator, biological attainability, optimal rule, universal state sufficiency or new paper is claimed. Changes can include tails, multimodality, duplicates and individual losses together. Covariance matching holds at the intervention instant; later moments may diverge. The historical inputs and continuation randomness are reused, so this is not independent training replication.

## Authenticated sources and fixed roster

Use the executor's `outputs/mismatch_mechanism_switch_v1/` accepted002package. Its delivery-manifest SHA-256 is `c6d376ce583e3abefd07115089f5a8012796b81d8cd81a585b640404c631dba4`. `ORG-STATE-SHAPE-064-INPUT_BINDINGS.json` authenticates the ten required files against original SOURCE/RESULT/DELIVERY manifests. In particular:

* `checkpoints.jsonl.gz`: `16e0af05018509a680825f1d3954001bd11f8ad505a49e7e3516339a3386a58f`.
* `outcomes.jsonl.gz`: `57a22d9c6374fb216ce9aa53d831aabf5b5daaf7c4459d3524d1de992b65d381`.
* `roster.json`: `969897be38b1df8c7014cf5f62c7dce097f5f5f00a8243815af74e856a8a0ad8`.

Retain all3,072rows keyed by `(regime,history,family,task)`: structured/isotropic regimes, history0–23, families `0,15,30,45,60,75,90,isotropic` in that order, and trial task0–7. The last family is the existing uniform-direction reference; its literal target records remain unchanged. Copy targets, historical angle, old mutation/survival seeds and both generation5O/R trait populations verbatim. No favorable subset, new training, target resampling or reshaping-strength selection.

Native references are the four stored002continuations OO,OR,RO,RR, including generation5–25measurements. Do not run them again. All eight new comparison cells use identical outcome definitions. The original003review is motivation, not a source of new numerical controls or new bootstrap draws.

## One orthogonal row-space transformation

N=32. Let X be an N-by-2 trait matrix, μ its column mean, D=X−1μ. Define the fixed N-by-(N−1) Helmert basis U, using zero-based column j=0…30:

* Rows i≤j: `U[i,j] = 1/sqrt((j+1)*(j+2))`.
* Row i=j+1: `U[i,j] = -(j+1)/sqrt((j+1)*(j+2))`.
* Later rows: zero.

For each distinct `(history,family,task)`, generate one31-by-31standard-normal matrix G with Python `random.Random(shape_seed).gauss(0.,1.)`, in row-major order. Obtain Q by **two-pass modified Gram–Schmidt on columns in increasing order**, using `math.fsum` dot products and positive Euclidean norms. No pivoting, sign forcing on Q, determinant conditioning, regularization or redraw. In exact arithmetic this is the positive-diagonal QR convention and produces Haar O(31) from ideal independent Gaussian input. Finite PRNG/floating arithmetic is the implemented approximation, not an exact real-randomness claim. `work/shape064_reference.py` fixes the actual algorithm and contrast ordering; copy it authentically into the source package or document a byte-bound equivalent wrapper.

The shape seed is the first16hexadecimal digits of SHA-256 of the UTF-8 string

`2026092564|state-shape064-row-orthogonal|history|family|task`,

converted to an integer. Fields use ordinary `str()` formatting; family is its roster string. Regime, O/R donor, and later rule are deliberately omitted: the same Q is shared across both regimes, both source states and both later rules. There are exactly1,536unique shape seeds and1,476,096new Gaussian API calls for their G matrices. Save the seed registry and the Q actually used; do not keep drawing until a convenient shape occurs.

Transform each source state once:

`X_SHAPE = 1μ + U Q U-transpose D`.

Use `math.fsum` for μ and matrix dot products as in the reference helper. There is no covariance inverse or eigenvalue truncation. Rank-deficient/zero-dispersion empirical states are retained; an identical-point state is unchanged mathematically. Reinsert the common later angle afterward, using the original set_rule convention. Native states use their original coordinate bytes, without centering and reconstructing them.

The full row operator is `11-transpose/N + UQU-transpose`; it is orthogonal and fixes the constant vector. Thus centroid, denominator-N trait covariance, and every fixed quadratic mean loss are identical mathematically at generation5. This is a transformation among individual rows, not a rotation of trait axes or targets. The finite transformed cloud is not an independent Gaussian sample and need not have zero skewness or Gaussian fourth moments.

Require all values finite and `max|Q^T Q−I| ≤ 2e-12`. Check both Q^TQ and QQ^T. Check constructed basis orthogonality/zero column sums within2e-12. At **every** transformed scientific checkpoint, require absolute differences of centroid coordinates, each covariance entry and normalized quadratic mean loss ≤1e-12 compared with the source's corresponding computations. Also verify the original loss=centroid-loss+dispersion-loss identity at1e-12throughout. Do not relax tolerances after outcomes. Zero/nonfinite QR norm or failed identities cause a preserved technical failure, not a redraw or outcome-based omission.

## Eight cells and unchanged continuations

Cells are `NATIVE_OO,NATIVE_OR,NATIVE_RO,NATIVE_RR,SHAPE_OO,SHAPE_OR,SHAPE_RO,SHAPE_RR`. The two letters identify source generation5state and later rule. Native cells map exactly to stored002OO/OR/RO/RR. Each source O/R is reshaped once, and copied into its two later-rule branches. No coordinate array may be shared mutably between branches.

Continue only the four SHAPE cells through generations6–25. Every member, including retained parents, has absolute angle phi for O or phi+pi/2 for R. Angles remain fixed as in002; do not import the heterogeneous inherited-angle011operator. Keep population32, one child per parent, major/minor proposal SD0.12/0.02, the literal metric matrix, normalized quadratic loss and coefficient10.0. The original `model.advance`, proposal, normalized_loss and sequential weighted-without-replacement selection define the scientific operator. Retain negative improvement and declining performance.

Restore both Python RNG states from each checkpoint, recursively converting saved JSON lists to tuples where required; preserve the Gaussian cache. For each generation generate the original32normal pairs and32survival uniforms once and share by current parent position across all four SHAPE cells. This recreates old continuation values, not new independent continuation seeds. Never consume shape-generation or bootstrap draws from these streams. Reference controls remain stored. At endpoint use the original performance

`Y = 1 − mean((x−target)^T H (x−target)) / (target^T H target)`.

The denominator is the original zero-state reference, not each arm's own starting loss. Initial performance must match NATIVE/SHAPE within each source, but later performance is unconstrained. Only generation25outcomes enter inferential estimates. Keep descriptive generation5–25performance, centroid, covariance and loss components without adding a second inferential endpoint.

## Exactly20metrics per group and380estimates

For every row, the20metrics are the8cell values, followed by:

* Four `F_s_t = Y_t,s,O − Y_t,s,R`, for source s=O/R and shape t=NATIVE/SHAPE.
* Two `J_t = F_O,t − F_R,t`.
* Four `G_sr = Y_NATIVE,s,r − Y_SHAPE,s,r`.
* `DELTA = J_NATIVE − J_SHAPE = G_OO−G_OR−G_RO+G_RR`.
* `G_MEAN = (G_OO+G_OR+G_RO+G_RR)/4`.

The reference helper fixes serialized names `F_O_NATIVE,F_O_SHAPE,F_R_NATIVE,F_R_SHAPE,J_NATIVE,J_SHAPE,G_OO,G_OR,G_RO,G_RR,DELTA,G_MEAN`, after the eight cells. Preserve both factorial identities. G_MEAN is a performance companion, not a replacement for the interaction primary.

Average eight paired trials within each regime/history/family first. Report20metrics in each of16regime-by-family groups (320estimates). Within each history, average the eight families **equally** to make ALL8, then report20metrics for each regime's ALL8group (40more). Finally report the20paired structured-ALL8 minus isotropic-ALL8contrasts (20more). Total380means/intervals. **Primary: structured|ALL8|DELTA.** ALL8defines the equally weighted existing test panel, not a naturally sampled distribution of task types. Preserve all family effects if averaging hides opposing signs.

Use a single stored2000-by-24bootstrap index matrix: `random.Random(2026092565)`, row-major calls to `randrange(24)`. These same resampled history indices apply to every cell, family and regime, respecting shared original streams and newly paired shapes. Histories h0–23are the fixed paired block labels across the two regimes; do not resample individual trials or treat families as independent replication. Use the original linear-interpolated2.5/97.5percentiles. Classify lower>0positive, upper<0negative, otherwise unresolved. Intervals are approximate pointwise exploratory95%, not simultaneous coverage. No p-value, posterior probability, multiplicity-adjusted discovery count, favorable-seed extension or equivalence claim is added.

This common bootstrap is new and prospectively fixed; it is not the002/003per-group sequence. Preserve old native outcomes and means, but do not require old interval endpoints or marginal sign classifications to remain identical. Report the direct regime contrast rather than inferring it from separate intervals. Units are normalized performance fractions, optionally multiplied by100for percentage points.

## Fixed counts and resource envelope

The design fixture's counts file is authoritative arithmetic:

| Quantity | Fixed count |
|---|---:|
| Historical sources / paired history blocks | 48 / 24 |
| Roster pairs / distinct shape matrices | 3,072 / 1,536 |
| Transformed generation5source states | 6,144 |
| New continuations / stored-control continuations | 12,288 / 12,288 |
| New updates / offspring / candidate scores | 245,760 / 7,864,320 / 15,728,640 |
| New selected-state snapshots, including generation5 | 258,048 |
| New selected coordinate values | 16,515,072 |
| New shape Gaussian API calls | 1,476,096 |
| Reused normal/uniform calls if regenerated per roster row | 3,932,160 / 1,966,080 |
| Inferential means/intervals | 380 |

Original mutation and survival seeds each have1,536unique values, reused across the two regimes. The listed call counts distinguish per-roster regeneration from distinct random values; they are not new independent random input. Save all48,000bootstrap indices. Deterministic measurements and fixture/audit work are additional operations, not extra population paths.

One production allocation: **1CPU,4GiB,30minutes**. Set numerical-library thread counts to one if any wrapper imports them; the reference sampler needs only the standard library. Stream by history/pair rather than retain all selected populations in memory. Scientific/source/report delivery cap: **512MiB** including copied compact source/control inputs and compressed raw selected states/indices. The new coordinates alone are about126MiB as float64; compact gzip or binary arrays make the cap feasible. Report actual file sizes and peak/resource accounting. This is a finite deliverable budget, not an inherited16MiB cumulative pre-write cap across unrelated writers or scheduler streams. The old config's8MiBfield belonged to a different older package and does not replace this064budget; preserve it in authenticated input rather than silently editing the source.

Use executor `outputs/population_shape_v1/` and HPC `experiments/population_shape_v1/` below the existing organized-variation-transfer root. Do not overwrite an existing package. One durable RUN_STARTED receipt and one scheduler submission. No automatic second job, timeout/precision/sample extension or new scientific variant after failure; preserve the concrete failure for the supervisor. Never duplicate a pending or unknown submission. Routine polling, retrieval and hashing belong in idempotent deterministic adapters, not recurring LLM checks.

## Fixtures, saved evidence and focused audit

The supervisor's design check passed2,314constructed/metadata assertions; maximum toy floating discrepancy3.56e-15. It authenticated inputs and parsed roster metadata without applying Q to scientific checkpoint states or running continuations. The initial checker failure is preserved: an exact-rational fixture accidentally used floating `fsum`; the checker was corrected to exact Fraction summation without relaxing any tolerance or changing the transformation.

Executor fixtures must cover the frozen sampler/seed registry and signs, zero/rank-deficient trait states, no shared mutable branches, full homogeneous angle replacement, checkpoint RNG restoration including the Gaussian cache, exact stored-control extraction, all20metric identities, ALL8weights and bootstrap pairing. Use constructed inputs; no production-outcome pilot. Do not regenerate the original002/003experiment for testing.

Save authentic source/configuration/input bindings, shape seeds and actual Q matrices, all transformed generation5states, stored native endpoint/control measurements, all new selected traits and candidate-selection indices at generations6–25, per-generation measurements, all pair endpoints, history/group tables, bootstrap rows,380estimates, tests, job/resource records and manifests. The immutable original checkpoint RNG states plus retained source regenerate proposals and uniforms; duplicate full candidate pools need not be stored. Make file-to-row mappings explicit and retain every adverse/unresolved outcome.

The supervisor audit independently reconstructs all380means/intervals, all6,144initial moment/score invariants, and the fixed raw block **history0, both regimes, all eight families and eight trials**:128roster pairs,256reshaped donor states,512new paths,10,240updates and655,360candidate scores. Audit that block's64unique sampler matrices from their fixed seeds, checkpoint RNG draws, survivor indices and selected traits without importing the producer's new implementation. Stored original operators define the model, but the raw checker must calculate their operations separately. Compare raw state/score arithmetic at1e-12and survivor indices exactly; document any platform difference without hiding a changed state. Expand only for an actual discrepancy. No complete rerun or full003audit.

Deliver one focused report with the fixed primary, every conditional group, G_MEANcompanion, moment-matching errors, future divergence and all failures. Two concise plots—conditional DELTAwith pooled contrasts, and initial-match/later-state diagnostics—are enough; do not create a new manuscript by default.

## Handoff and ownership

Executor task `01a0c171-4f3a-7082-a8d6-f1505334f441` owns implementation/testing. Its last confirmed environment lacked SSH: do not repeat denied probes. Build the frozen package locally and write a genuine `LOCAL_HANDOFF.json` with source hashes, task hash, real submission state and the exact idempotent supervisor adapter command. Notify the supervisor directly. The supervisor can use its existing SSH access for that same tested handoff. A handoff is not a completed scientific result. Keep old executor polling paused and leave supervisor-owned coordination, original handoffs and public files untouched.

Stop execution after this finite assignment. The supervisor owns result interpretation, source/audit acceptance, HPC verification and the next concrete decision. No extra covariance target, shape strength, angle, training cohort, continuation count or publication is automatically authorized.
