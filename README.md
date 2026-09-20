# Parkinsonian Gait Biomarkers

Reproducible secondary-analysis pipeline for separating candidate gait measures
that remain associated with Parkinsonian motor severity across contexts from
measures dominated by task, speed, site, or short-term state.

## Current evidence status

The authorized analysis is complete. In the primary WearGait V1 reference
walkway analysis (124 SP/HP rows from 62 PD participants), several measures
were associated with MDS-UPDRS Part III gait-item severity; **no feature met
the full context-robust trait criterion**. CARE-PD provides a limited,
translation-only directional check, not a matched feature replication. Read
[the full report](report/AAN_report.md) before using these findings.

## Run

```bash
python3.11 -m unittest discover -s tests -v
python3.11 scripts/acquire_dataset_metadata.py
bash scripts/reproduce_final_results.sh
```

Keep authorized, non-redistributable files outside the repository (for example
in controlled Drive storage), then set `PARKINSON_GAIT_DATA_ROOT` to the folder
containing `WearGait_PD_V1`, `WearGait_PD_Longitudinal`, and `CARE_PD`.

```bash
export PARKINSON_GAIT_DATA_ROOT="/path/to/authorized/Parkinsonian_Gait_Data"
bash scripts/reproduce_final_results.sh
```

The pipeline writes row-level audit files locally under `results/` (ignored by
Git) and the public-safe aggregate decision record at
`results/frozen/results.json`.

## Design safeguards

- Reference outcomes are PKMAS pressure-walkway measurements; contacts are a
  separately validated temporal layer.
- Participant-level bootstrap resamples whole participants, not walks.
- GEE clusters repeated task rows by participant and adjusts for task, site,
  age, height, and sex.
- Benjamini-Hochberg FDR correction is applied across the primary feature family.
- The project reports association, not diagnosis, causality, or medication effect.

The preregistered design is in `docs/preregistration.md`; feature compatibility
across WearGait and CARE-PD is in `docs/common_feature_mapping.md`; sources and
scientific boundaries are in `research_review_parkinsonian_gait.md`.

## Conclusion

The stronger trait-biomarker hypothesis was not supported under the frozen
conjunction. This is a useful negative result: severity associations alone are
not enough to claim context robustness or clinical readiness.
