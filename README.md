# Parkinsonian Gait Biomarkers

Reproducible secondary-analysis pipeline for separating candidate gait measures
that remain associated with Parkinsonian motor severity across contexts from
measures dominated by task, speed, site, or short-term state.

## Current evidence status

The authorized v3.2.4 integration release is complete. In the primary WearGait V1 reference
walkway analysis (124 SP/HP rows from 62 PD participants), several measures
were associated with MDS-UPDRS Part III gait-item severity; **no feature met
the full context-robust trait criterion**. CARE-PD provides a limited,
translation-only directional check, not a matched feature replication. Read
[the full report](report/AAN_report.md) before using these findings.

### v4 prospective extension

The separately frozen v4.0.6 redesign tested new candidates without changing
the v3.2.4 result. A control-trained, severity-blind Context-Adjusted Gait
Deviation Score was associated with gait-item severity (standardized GEE
effect 0.301, 95% CI 0.089–0.513, q=0.0055) and remained associated after
speed adjustment. It is **not** yet a qualified trait biomarker: repeatability
and transport gates remain unestimated. Prespecified speed-scaling candidates
were not associated after family-level FDR. The long-bout, arm/axial, and
harmonic sensor candidates are explicitly `NOT_ESTIMABLE` in this release,
not negative findings, because the eligible free-walk recordings did not meet
the required model sample size and have no validated speed covariate.

Mobilise-D half-sample stability independently favored walking speed and stride
length over cadence and stride duration. See the frozen
[v4 report](results/v4/frozen/AAN_v4_report.md), [evidence matrix](results/v4/frozen/evidence_matrix.csv),
and [five figures](results/v4/frozen/figures).

## Run

```bash
python3.11 -m unittest discover -s tests -v
python3.11 scripts/acquire_dataset_metadata.py
bash scripts/reproduce_final_results.sh
```

Keep authorized, non-redistributable files outside the repository (for example
in controlled Drive storage), then set `PARKINSON_GAIT_DATA_ROOT` to the folder
containing `WearGait_PD_V1`, `WearGait_PD_Longitudinal`, `CARE_PD`,
`MobiliseD_CVS_v1_0_0`, `Mendeley_Gait_PD_v2`, and `AdaptiveDBS_Gait_2026`.

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
- Participant-level bootstrap and permutation resamples use the declared GEE,
  deterministically sharded across workers; they never substitute OLS.
- GEE clusters repeated task rows by participant and adjusts for task, site,
  age, height, and sex.
- Benjamini-Hochberg FDR correction is applied across the primary feature family.
- The project reports association, not diagnosis, causality, or medication effect.
- The V2 clinical-change estimand is `NOT_ESTIMABLE_AFTER_ARCHIVE_AND_SCHEMA_AUDIT`;
  it was unavailable in the authorized release, not a failed validity test.

The preregistered design is in `docs/preregistration.md`; feature compatibility
across WearGait and CARE-PD is in `docs/common_feature_mapping.md`; sources and
scientific boundaries are in `research_review_parkinsonian_gait.md`.

## Conclusion

The stronger trait-biomarker hypothesis was not supported under the frozen
conjunction. This is a useful negative result: severity associations alone are
not enough to claim context robustness or clinical readiness.
