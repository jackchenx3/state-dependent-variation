# Population state changes the transfer value of organized variation in a finite-population model

Jack Chen | Research preprint v1.0 | 22 September 2026

[Manuscript](paper/MANUSCRIPT.md) · [PDF](paper/MANUSCRIPT.pdf) · [Supporting information](paper/SUPPLEMENT.md) · [Evidence index](provenance/STUDIES.json)

Historically acquired variation biases can facilitate adaptation, but their value may change as a population moves through a new environment. We studied a two-dimensional model comparing an inherited variation orientation with a quarter-turned control of identical covariance eigenvalues. Transfer comparisons showed conditional benefits and relative harms across target directions. An exact starting-state expectation of offspring weight predicted early population rankings well but underperformed a simpler directional predictor at generation 25. Crossed interventions then showed that the later rule effect depends on both the generation-5 centroid and the complete centered population configuration. On 48 freshly trained histories, fixed prospective choices using the empirical population improved generation-25 performance over centroid-only choices by 0.55–0.59 percentage points of initial normalized loss. Gaussian moments achieved most of this incremental gain. The improvement fell below the prespecified two-point target, unconditional switching was already strong, and subgroup harms remained. Independent continuations from fixed checkpoints then identified both local expected-contrast discrepancy and changes in conditional rule ranking between one step and the terminal horizon. More detailed local policies improved one-step effect-size calibration but worsened terminal calibration, despite fewer resolved terminal ranking contradictions. These results distinguish conditional state effects, prospective policy value, contrast calibration and ranking across horizons. Their scope remains the specified finite-population model; they identify neither a unique mediator nor a generally optimal adaptive policy.

## Reproduce the saved analyses

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_statistics.py
python scripts/rebuild_figures.py
python scripts/verify_release.py
```

The package contains complete statistical grids, block/history aggregates, original bootstrap rows or exact archived-seed replays, archived code and source provenance. These commands do not execute population dynamics. Large raw trajectories and random tapes are excluded; full raw-trajectory replay is not claimed. See [data availability](docs/DATA_AVAILABILITY.md) and [AI assistance](docs/AI_ASSISTANCE.md).

Manuscript/figures/data: CC BY 4.0. Original code: MIT. This work has not undergone external peer review. A Zenodo DOI will be added after publication.
