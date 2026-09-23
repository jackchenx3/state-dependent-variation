# Noise correction and error identity

Condition on a fixed checkpoint and frozen analytic contrast a. For R independent paired evaluation replicates let μ_g=E[D_gj], σ_g²=Var(D_gj). Then E[(a−Dbar_g)²]=(a−μ_g)²+σ_g²/R, while E[s_g²]=σ_g². Thus B_g=(a−Dbar_g)²−s_g²/R is unbiased for (a−μ_g)². This requires finite second moments and independent replicates, not Gaussian population traits or a Gaussian contrast distribution. Pairing O/R within a replicate is deliberately preserved; s_g² is the variance of their difference, not the sum of independent-arm variances.

Apply the same calculation to Z_j=D_25,j−D_6,j, whose two horizons share the replicate: H=(Zbar)²−s_Z²/R is unbiased for (μ_25−μ_6)². Since s_Z²=s_25²+s_6²−2s_6,25, preserving the cross-horizon covariance is essential.

With e=a−Dbar_6 and d=Dbar_25−Dbar_6, direct expansion gives

X=B_25−B_6−H=−2[e d+(s_6,25−s_6²)/R].

Consequently E[X]=−2(a−μ_6)(μ_25−μ_6). The exact estimate identity B_25=B_6+H+X can contain cancellation. These quantities are mathematical squared-error components, not disjoint causal mechanisms or mediation percentages. An average signed discrepancy can cancel across checkpoints even when average squared discrepancy is large.

Unbiased squared-effect estimators can be negative at finite R. Retain them; flooring introduces bias, and taking a square root is undefined for negative estimates. The history bootstrap summarizes this frozen checkpoint panel and retains evaluation Monte Carlo variability rather than removing all uncertainty about the latent process expectations.

The local mixture formula and the expected sequential finite-pool without-replacement process need not coincide. B_6 estimates their expected-contrast discrepancy at N=32, not simply sampling noise and not an infinite-population limit. B_25 additionally reflects changed conditional rule value over the remaining horizon. Neither calibration quantity alone proves an incorrect rule ranking; the separate conditional intervals and full cross-tabulation address that question with approximate Monte Carlo coverage.
