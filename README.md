# Population state changes the transfer value of organized variation in a finite-population model

Jack Chen | Research preprint v1.1.0 | 25 September 2026

[Manuscript](paper/MANUSCRIPT.md) · [PDF](paper/MANUSCRIPT.pdf) · [Supporting information](paper/SUPPLEMENT.md) · [Evidence index](provenance/STUDIES.json)

Historically acquired variation biases can facilitate adaptation, but their value may change as a population moves through a new environment. We studied a two-dimensional model comparing an inherited variation orientation with a quarter-turned control of identical covariance eigenvalues. Transfer comparisons showed conditional benefits and relative harms across target directions. An exact starting-state expectation of offspring weight predicted early population rankings well but underperformed a simpler directional predictor at generation 25. Crossed interventions then showed that the later rule effect depends on both the generation-5 centroid and the complete centered population configuration. A further row-space intervention preserving initial mean, full trait covariance and quadratic loss reduced the magnitude of the structured-history interaction by 0.74 percentage points, while a large interaction persisted and the direct regime difference remained unresolved. On 48 freshly trained histories, fixed prospective choices using the empirical population improved generation-25 performance over centroid-only choices by 0.55–0.59 percentage points of initial normalized loss. Gaussian moments achieved most of this incremental gain. The improvement fell below the prespecified two-point target, unconditional switching was already strong, and subgroup harms remained. Independent continuations from fixed checkpoints then identified both local expected-contrast discrepancy and changes in conditional rule ranking between one step and the terminal horizon. More detailed local policies improved one-step effect-size calibration but worsened terminal calibration, despite fewer resolved terminal ranking contradictions. These results distinguish conditional state effects, prospective policy value, contrast calibration and ranking across horizons. Their scope remains the specified finite-population model; they identify neither a unique mediator nor a generally optimal adaptive policy.

## Reproduce the saved analyses

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_statistics.py
python scripts/rebuild_figures.py
python scripts/verify_release.py
```

The unified commands recompute 8,320 mean/interval records and regenerate all nine figures from stored aggregates and bootstrap rows. They do not simulate populations. Large raw trajectories/checkpoints and Q matrices are excluded. See [data availability](docs/DATA_AVAILABILITY.md), [064 result note](provenance/064_RESULTS_NOTE.md), [administrative source substitutions](provenance/ADMINISTRATIVE_SUBSTITUTIONS_064.json) and [AI assistance](docs/AI_ASSISTANCE.md). Archived execution code is source for inspection, not a turnkey raw-run claim.

Version DOI: [10.5281/zenodo.22956936](https://doi.org/10.5281/zenodo.22956936). [Previous v1.0.0](https://doi.org/10.5281/zenodo.22907602) remains unchanged. All versions: [concept DOI](https://doi.org/10.5281/zenodo.22907601).

Manuscript/figures/data: CC BY 4.0. Original code: MIT. Not externally peer reviewed; AI assistance disclosed.

## Related preprints

[Shared-cache search](https://github.com/jackchenx3/memory-and-fresh-search) · [Private-memory transmission](https://doi.org/10.5281/zenodo.22950710). These papers have distinct model/evidence scopes; versions are not additional papers or independent replications.
