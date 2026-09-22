# AAN v4.5 scientific repair

This correction preserves the v4.1 score and historical v4.4 results. The [FDA dataset description](https://cdrh-rst.fda.gov/weargait-pd-longitudinal-multi-session-wearables-dataset-gait-parkinsons-disease) states that the minimum interval between sessions was six months, so the ICC estimates longitudinal score stability under changing clinical conditions. Short-term, state-controlled test–retest reliability is unmeasured. Neither task meets the frozen ICC lower-bound criterion of 0.80.

| Task | Paired participants | Six-plus-month ICC(A,1), percentile 95% CI | BCa 95% CI sensitivity | Paired difference SD | Four-pass conditional bootstrap SD, median | Longitudinal MDC95 equivalent |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| SelfPace | 45 | 0.647 (0.331 to 0.819) | 0.439 to 0.863 | 1.059 | 0.427 | 2.076 |
| HurriedPace | 44 | 0.282 (-0.001 to 0.547) | -0.009 to 0.543 | 1.173 | 0.524 | 2.299 |

The conditional bootstrap resamples the four observed passes, recomputes the median of each of the eight input features, then applies the SHA256-checked frozen model. It estimates pass-selection precision conditional on those passes. The paired-difference SD and its 1.96 multiple include disease change, medication/state differences, and measurement noise; they are **not** pure SEM or MDC for a stable clinical state. The v4.4 pass-score ANOVA's SEM, MDC95 and G coefficient used a mean-of-four residual rule and must not be used for this nonlinear endpoint. The pass-score variance components remain descriptive only. Three session files had only three valid passes; with so few exclusions, the selection effect cannot be estimated reliably.

## Sources of observed variation

| Task | Between-person endpoint SD | Between-visit difference SD | Within-session single-pass-score SD |
| --- | ---: | ---: | ---: |
| SelfPace | 1.136 | 1.059 | 0.872 |
| HurriedPace | 0.788 | 1.173 | 1.029 |

These SDs describe different units and are not additive variance components. Across 89 participant-visits with both tasks, the hurried-minus-self endpoint contrast averaged -0.190 (SD 1.276). Medication and other visit-state effects cannot be separated without session-linked anchors. The sizeable between-visit spread gives no empirical basis for claiming that additional passes alone would qualify a stable trait score.

## Four-pass complete-case check

| Task | Group | Participants | V1 gait item available | Median V1 gait item | Mean V1 age |
| --- | --- | ---: | ---: | ---: | ---: |
| HurriedPace | complete_pair | 44 | 42 | 1.0 | 66.6 |
| HurriedPace | excluded_four_pass | 2 | 2 | 0.5 | 67.0 |
| SelfPace | complete_pair | 45 | 43 | 1.0 | 66.5 |
| SelfPace | excluded_four_pass | 1 | 1 | 2.0 | 74.0 |

Only three participants were excluded for lacking the fourth valid pass, so this is a descriptive selection check, not a statistical test. V1 clinical scores are linked by identifier; their assessment dates have not been shown to coincide with longitudinal session 1.

## Clinical-source audit

The authorized longitudinal manifest lists 1069 files. The audit inventoried 860 CSVs, read 186 of 186 relevant SelfPace/HurriedPace headers, inspected 93 of 93 session MAT top levels, and read nested task fields in 93 structures. 48 cloud MAT files required fresh temporary Synapse copies; 0 remained unreadable. MAT variables and task fields are recorded in [source_audit.json](source_audit.json). No verified repeated session-level MDS-UPDRS, medication dose/timing, or DBS variable was identified. 46 session-1 identifiers match the V1 clinical table, but identifier overlap does not establish matched assessment dates and provides no session-2 clinical score. Clinical responsiveness remains `NOT_ESTIMABLE`. The `ClinicalEvent` CSV field is a task annotation stream, not a clinical rating.

## CARE-PD transport and medication challenge

The released CARE-PD pickles include canonical SMPL pose/translation and some UPDRS/medication labels. These do not by themselves reproduce the eight frozen PKMAS gait inputs. All eight measurement equivalence gates remain unvalidated in [source_audit.json](source_audit.json). Accordingly, a frozen-score CARE-PD leave-one-center-out analysis and paired OFF/ON score responsiveness are `NOT_ESTIMABLE`. Running either analysis without that outcome-blind measurement bridge would manufacture comparability. The existing CARE-PD translation-speed associations remain separate exploratory evidence.

The v4.4 VA Seattle holdout shows association transport at one overlapping site. Its within-site standardized association does not test whether the absolute normative score is calibrated at that site, and one site cannot establish general transport.

## H2 reporting correction

Favorable calibration is now scored by distance to intercept 0 and slope 1. In the 100 stored repeated participant-grouped validations, the corrected fractions are:

| Unit | Slope closer to 1 | Intercept closer to 0 |
| --- | ---: | ---: |
| Participant | 60% | 61% |
| Row | 21% | 22% |

The ranking advantage remains; this correction does not establish better absolute clinical-score prediction. No severity outcome was used to choose a CARE-PD feature transform, site map, or reference threshold.

## Conclusion

The score has a validated WearGait eight-input reconstruction and reproducible incremental severity ranking. Its six-plus-month stability fails the frozen trait threshold. Short-term reliability, clinical responsiveness, and multi-center frozen-score transport require additional comparable measurements. HurriedPace may be investigated as a motor challenge in a future registered study, but this release does not claim a challenge-response biomarker.
