# Fixed Gaussian parent/offspring mixture functional

For Gaussian X~N(m,T), set residual r=m−t. Multiplying its density by exp(−beta (X−t)ᵀA(X−t)) and completing the square gives K=(I+2 beta T A)⁻¹, selected residual mean Kr and covariance V=KT. T A order matters when matrices do not commute. For positive-definite T this follows from the precision T⁻¹+2 beta A; the stated form extends continuously to positive-semidefinite/singular T without inverting it.

The expected unnormalized weight is Z=det(I+2 beta T A)⁻¹/² exp(−beta rᵀAKr). The mean loss within that ideally reweighted component is q=(Kr)ᵀA(Kr)+tr(AV). At T=0, Z=exp(−beta rᵀAr) and q=rᵀAr, the point-parent case. These are distinct quantities; choosing by Z alone is not this policy.

For an equal-prior mixture of components, posterior component masses are proportional to their Z values. Hence mean selected loss is sum(Z_j q_j)/sum(Z_j). Subtract max(log Z) before exponentiation for stability. M applies this to centroid point-parent and Gaussian offspring; G to Gaussian parent/offspring moment approximations; E to all point parents and their Gaussian offspring. The common parent/offspring prior mass is 1/2 in every policy, and every member is equally weighted within the empirical mixture.

The Gaussian integral and mixture arithmetic are exact for their specified infinite normalized-weight distribution. The finite experiment instead generates a sampled offspring pool, retains parents as candidates, and draws survivors sequentially without replacement; the functional therefore approximates that selection operation. It also forecasts one ideal selection step, not the generation-25 endpoint. Increased input detail need not improve the finite-horizon policy.

The independent audit uses a different evaluation: write A=BᵀB by Cholesky, transform residual u=Br and covariance W=BTBᵀ, then evaluate the symmetric (I+2 beta W) system. This avoids covariance inversion at singular T and checks noncommuting product order. Focused tests additionally integrate a noncommuting Gaussian fixture by deterministic two-dimensional quadrature. No formula is fitted to transfer outcomes.
