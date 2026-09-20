# Parkinsonian Gait Biomarkers

Reproducible secondary-analysis pipeline for separating candidate gait measures
that remain associated with Parkinsonian motor severity across contexts from
measures dominated by task, speed, site, or short-term state.

## Current evidence status

The repository is operational and tests use synthetic, non-clinical fixtures.
The study hypothesis has **not been tested** because WearGait-PD,
WearGait-PD Longitudinal, and CARE-PD participant files require separate
data-access/terms steps. No clinical result, trait marker, or AAN result is
claimed in this state. See [DATASETS.md](DATASETS.md) for the recorded access
boundary and `results/frozen/results.json` for the machine-readable status.

## Run

```bash
python3.11 -m unittest discover -s tests -v
python3.11 scripts/acquire_dataset_metadata.py
bash scripts/reproduce_final_results.sh
```

Place only authorized, non-redistributable files in `data/raw/`; it is ignored
by Git. The pipeline reads CSV input described in `configs/analysis.yaml` and
writes an aggregated feature table, adjusted association table when adequate
clinical data are present, and a frozen manifest to `results/`.

## Design safeguards

- Participant-level bootstrap resamples whole participants, not walks.
- Context/site/demographic covariates are explicit; participant IDs never
  stand in for sites.
- Benjamini-Hochberg FDR correction is applied across the primary feature
  family.
- The project reports association, not diagnosis, causality, or medication
  effect.

The preregistered design is in `docs/preregistration.md`; feature compatibility
across WearGait and CARE-PD is in `docs/common_feature_mapping.md`; sources and
scientific boundaries are in `research_review_parkinsonian_gait.md`.

## Conclusion

As of the metadata-only release state, the only valid conclusion is that the
planned trait-versus-state hypothesis remains unevaluated. The repository
preserves this negative operational finding instead of substituting simulated
or unrelated data for clinical evidence.
