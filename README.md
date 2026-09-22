# Parkinsonian Gait Biomarkers

Reproducible secondary-analysis pipeline for separating candidate gait measures
that remain associated with Parkinsonian motor severity across contexts from
measures dominated by task, speed, site, or short-term state.

## Current evidence status

The primary WearGait V1 analysis contains 124 SP/HP rows from 62 PD
participants. Several measures were associated with MDS-UPDRS Part III gait-item
severity, but **no feature met the full context-robust trait criterion**.
CARE-PD remains a limited translation-only directional check, not a matched
feature replication. The newest evidence is the [v4.5 scientific correction](results/v4_5/AAN_v4_5_report.md).

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

### v4.1 tightly scoped validation

v4.1.0 validates, but does not replace, the v4.0.6 score. Across 2,000
healthy-reference participant resamples, the score retained the positive
severity-association direction in every resample (median standardized effect
0.291). In five-fold participant-grouped prediction, adding the score to gait
speed improved rank correlation but did not improve RMSE, so this sample does
not support incremental predictive value beyond speed. Mobilise-D's
within/between model showed stable within-person effects for gait speed and
stride length, while cadence and stride duration were inconclusive. WearGait
repeated-session scoring and eight-input external transport remain explicitly
`NOT_ESTIMABLE`; no crosswalk or reference model was improvised. Read the
[v4.1 report](results/v4_1/frozen/AAN_v4_1_report.md), its
[frozen manifest](results/v4_1/frozen/protocol_manifest.json), and the
[five v4.1 figures](results/v4_1/frozen/figures).

### v4.2 H4/H2 validation closure

v4.2.0 audited 1,600 V1 and 863 longitudinal raw walkway CSVs. Contact timing
is recoverable, but the released pressure-grid strings have no documented
calibration to metric rear-foot coordinates; all-eight PKMAS equivalence cannot
be validated, so H4 remains `NOT_ESTIMABLE`. Across 100 participant-grouped
five-fold repeats, the added score improved Spearman ranking in 99% of
row-level and 98% of participant-level analyses. It did not consistently
improve absolute error, so the frozen interpretation is
`RANKING_SUPPORT_ONLY`, not a full prediction pass. Read the
[v4.2 report](results/v4_2/frozen/AAN_v4_2_report.md), [frozen evidence
matrix](results/v4_2/frozen/evidence_matrix.csv), and the
[reporting addendum](docs/v4_2_reporting_addendum.md).

### v4.3 raw-walkway reconstruction closure

The documented WearGait Supplementary Table S5/Figure S5 coordinate contract
enabled an all-eight raw-to-PKMAS equivalence bridge: all eight inputs passed on
252 matched V1 trials. The frozen v4.1 score was then applied without refitting
to 182 longitudinal trials. H4 became estimable as six-plus-month longitudinal
stability but failed the strict ICC criterion: self-paced ICC(A,1)=0.707 (95% bootstrap CI 0.462 to
0.844) and hurried ICC(A,1)=0.390 (0.073 to 0.657). Read the [H4
closure](docs/v4_3_h4_reconstruction.md).

### v4.4 measurement-error and transport extension

v4.4 tested a new, prespecified four-valid-pass featurewise-median endpoint
without changing the v4.1 model or v4.3 conclusion. It did not rescue
reliability: self-paced ICC(A,1)=0.647 (95% CI 0.331 to 0.819) and hurried
ICC(A,1)=0.282 (-0.001 to 0.547), both below the frozen lower-CI threshold of
0.80. Its original SEM/MDC95 and G coefficient were later found not to match
the nonlinear four-pass median endpoint; use the v4.5 correction below. The result remains `FAIL`, not a revised
trait claim. A VA Seattle holdout whose control reference was derived only
from the other site, without clinical-outcome tuning, had a positive severity
association (effect 0.578, 95% CI 0.186 to 0.970) but is explicitly
`INCOMPLETE` because it is only one overlapping site. Linked repeated clinical
severity and medication-timing fields are absent from the authorized
longitudinal task schema, so responsiveness remains `NOT_ESTIMABLE`. See the
[v4.4 report](results/v4_4/AAN_v4_4_report.md), [evidence
matrix](results/v4_4/v4_4_evidence_matrix.csv), and [protocol](docs/v4_4_measurement_protocol.md).

### v4.5 scientific correction

The repeat visits are at least six months apart, so v4.3/v4.4 ICCs measure
longitudinal stability under uncontrolled clinical change. Short-term
test-retest reliability remains `NOT_ESTIMABLE`. v4.5 recomputes error on the
actual median-of-four-inputs → frozen-score endpoint and corrects H2 calibration
favorability against intercept 0 and slope 1. All 186 relevant task CSV headers
and all 93 session MAT structures were inspected; 48 MAT files required fresh,
temporary Synapse copies because the Drive cache timed out. No repeated clinical
anchor was verified. CARE-PD's eight-input measurement bridge is unvalidated, so
multi-center frozen-score transport and medication response remain unestimated.
See the [v4.5 report](results/v4_5/AAN_v4_5_report.md), [source audit](results/v4_5/source_audit.json),
and [evidence matrix](results/v4_5/evidence_matrix.csv).

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

To reproduce the v4.5 correction after the v4.3 equivalence QC is present:

```bash
PYTHONPATH=. python scripts/run_v4_4_measurement_protocol.py --v1-root "$PARKINSON_GAIT_DATA_ROOT/WearGait_PD_V1" --longitudinal-root "$PARKINSON_GAIT_DATA_ROOT/WearGait_PD_Longitudinal"
PYTHONPATH=. python scripts/run_v4_5_repair.py
PYTHONPATH=. python scripts/audit_v4_5_sources.py --data-root "$PARKINSON_GAIT_DATA_ROOT" --hydrate-unreadable
PYTHONPATH=. python scripts/generate_v4_5_report.py
PYTHONPATH=. python scripts/qa_release_gate.py
```

The source audit uses temporary Synapse copies only when Drive placeholders
cannot be read. It requires the dataset access already granted to the user.

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
