# An exact state-dependent rule comparison in an ideal Gaussian model

Prepared while ORG-STATE-003 executes, before inspecting its new outcomes. This is an analytical result and a candidate basis for a later prediction, not another execution assignment or a finding about the finite-population experiment. No new numerical population trajectory is generated here.

## Question and assumptions

Can the same fixed-spectrum variation rule have opposite effects solely because the population centroid changes? An ideal selected-population model gives an exact affirmative example and makes clear what covariance information could additionally matter.

Let the current trait distribution be Gaussian with mean m and covariance S. Let t be the target, A a symmetric positive-definite loss matrix, and beta > 0. Offspring receive independent zero-mean Gaussian variation with covariance C. Thus their preselection distribution is Gaussian with covariance T = S + C, assumed positive definite. Replace the whole population by the infinite-population distribution obtained by weighting offspring by exp[-beta (x-t)' A (x-t)] and normalizing. There is no retained-parent mixture and no finite sample or sequential sampling without replacement in this ideal model.

These distinctions matter: the actual experiments retain parent and offspring candidates and sample a finite pool without replacement. The result below is exact for the explicitly defined ideal model, not for that experiment.

## Completing the square

Write r = m-t and y = x-t. The unnormalized exponent is

`-0.5 (y-r)' T^{-1} (y-r) - beta y' A y`.

Consequently the selected distribution has covariance and residual mean

`V_C = (T^{-1} + 2 beta A)^{-1}`,

`k_C = V_C T^{-1} r = K_C r`, where `K_C = (I + 2 beta T A)^{-1}`.

The order of matrix products is essential when T and A do not commute. The exact mean selected loss is

`ell_C(r,S) = r' K_C' A K_C r + tr(A V_C)`.

For two variation rules O and R, define their performance contrast as selected loss under R minus selected loss under O. Then

`Delta(r,S) = r' [K_R' A K_R - K_O' A K_O] r + tr[A(V_R-V_O)]`.

For fixed S, this is a quadratic function of centroid residual r. Its zero set is a possibly degenerate quadric. Changing the centroid can therefore change the preferred rule when the quadratic and constant terms permit a crossing. Changing S alters both terms. There need not be a crossing for every choice of matrices; this is a conditional principle, not a universal reversal theorem.

This expression concerns the mean loss after selection. It is distinct from expected unnormalized offspring weight, the statistic used by the V3 local predictor.

## Exact two-dimensional example

Take A = I, beta = 1/2, S = 0, C_O = diag(1,1/4), and C_R = diag(1/4,1). Both rules have the same covariance eigenvalues and total variation. Selection gives

`K_O = diag(1/2,4/5)`, `V_O = diag(1/2,1/5)`,

with the diagonal entries interchanged for R. Hence

`Delta(r,0) = (39/100) (r_1^2-r_2^2)`.

At residual r=(1,0), selected mean losses are 19/20 for O and 67/50 for R, so O has a performance advantage of 39/100. At residual r=(0,1), these losses exchange and R has the same advantage. The centered starting configuration and the two rules are unchanged. The centroid alone reverses the one-step selected-population ranking in this ideal model. At equal squared residual coordinates, the two expected losses tie.

This is a constructed mathematical example, not a new HPC observation, independent replication, or parameterization fitted to the ORG-STATE-003 outcomes. It does not establish the cause or size of the observed generation-25 interaction.

## What this adds to the next decision

The derivation supplies a specific state-dependent mechanism to test: the useful orientation can depend on the current residual position rather than only the original target direction. In a Gaussian model, covariance also changes the comparison. In the actual finite empirical population, higher moments, the retained parents, sampling and the remaining horizon may matter as well.

ORG-STATE-003 should finish unchanged. If its centroid intervention changes rule value at fixed centered configuration, that is population evidence in the actual model, complementary to this mathematical example. If configuration or three-factor effects matter, a centroid-only description is insufficient. Either outcome remains informative.

A later predictive study could compare a frozen state-dependent selected-loss approximation with the original and current-state offspring-weight measures, but only if that comparison answers a distinct question. A local exact formula is not automatically a good longer-horizon policy: V3 already demonstrates this risk. Any policy study should use fresh frozen histories, declare whether target/metric access is available, account for information and evaluation costs, and judge its prespecified terminal outcome. No policy is selected or launched by this note.

The derivation is supplied in full rather than claimed as a new discovery or attributed to an unchecked source. It is a standard completion-of-the-square calculation applied to this explicitly defined limiting model. The existing literature context remains in ORG-MECH-002-next-design-context.md; novelty and empirical validity are separate questions.
