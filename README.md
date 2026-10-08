# Parkinsonian Gait Biomarkers

A reproducible study of whether a control-referenced gait measure captures Parkinsonian gait severity beyond walking speed, and whether that signal survives separate tests of robustness, measurement agreement, longitudinal stability, and transport.

## Research question

A gait measure can correlate with clinical severity without being reliable enough to monitor a person over time or transferable enough to use across settings. This project therefore treats biomarker validation as a sequence of distinct questions rather than a single performance metric.

The primary candidate, `context_adjusted_gait_deviation_v1`, is an eight-input distance from an age- and height-adjusted healthy-control gait reference. Parkinsonian outcomes are not used to fit the healthy reference.

## Main findings

| Evidence layer | Result |
|---|---|
| Concurrent severity association | Supported. Standardized effect 0.301, 95% CI 0.089 to 0.513, q=0.0055 |
| Association after gait-speed adjustment | Supported. Standardized effect 0.279, 95% CI 0.083 to 0.475, q=0.0053 |
| Healthy-reference robustness | Same association direction in all 2,000 control-reference resamples |
| Severity ranking beyond speed | Improved in 98% of participant-level repeated validations; median ΔSpearman +0.0474 |
| Exact-score prediction | Not established; RMSE and MAE did not improve consistently |
| Eight-input analytical reconstruction | All eight inputs passed prespecified agreement gates on 252 matched trials |
| Six-plus-month stability | Failed the prespecified criterion |
| Short-term test-retest reliability | Not estimable from the available repeated visits |
| Clinical responsiveness | Not estimable with verified session-linked clinical anchors |
| Broad external transport | Not established |

The long-interval result is important. Self-paced ICC(A,1) was 0.647 (95% BCa CI 0.439 to 0.863; n=45) and hurried-pace ICC(A,1) was 0.282 (95% BCa CI -0.009 to 0.543; n=44). Those visits were at least six months apart, so the result reflects stability under changing clinical conditions rather than a controlled short-term repeatability experiment.

## Scientific contribution

The contribution is not a claim that gait features, multivariate distance scores, or Parkinson digital biomarkers were invented here. It is the application of a fixed score to a prespecified validation architecture that separates:

1. concurrent clinical association,
2. robustness to the healthy reference sample,
3. information beyond a strong baseline such as gait speed,
4. analytical measurement agreement,
5. longitudinal behavior,
6. clinical responsiveness, and
7. external transport.

A positive result at one layer is not treated as evidence for the others. The six-plus-month stability test remained negative rather than being redefined after the result was observed.

This framing is consistent with the broader digital-biomarker literature. Recent reviews continue to identify limited external validation, heterogeneous methods, and insufficient longitudinal evidence as major barriers to clinical translation in Parkinson disease and neurological gait measurement:

- Rábano-Suárez et al., *Movement Disorders* (2025): [Digital Outcomes as Biomarkers of Disease Progression in Early Parkinson's Disease](https://pubmed.ncbi.nlm.nih.gov/39613480/)
- Qi et al., *Journal of Medical Internet Research* (2025): [Digital Biomarkers for Parkinson Disease](https://pubmed.ncbi.nlm.nih.gov/40392578/)
- Ortega-Robles et al., *Medical Sciences* (2026): [Walking as a Window to the Brain](https://pubmed.ncbi.nlm.nih.gov/42506308/)

See [research_review_parkinsonian_gait.md](research_review_parkinsonian_gait.md) for the literature context and claim boundaries.

## Study design

The primary WearGait-PD analysis includes 62 independent participants with Parkinson's disease and repeated walking tasks. Repeated task records are clustered by participant, and cross-validation splits keep all records from a participant in the same fold.

The frozen score uses eight gait inputs:

- gait speed
- cadence
- mean step length
- mean stride length
- mean step time
- mean stride time
- step-time coefficient of variation
- stride-time coefficient of variation

The healthy-control reference estimates the expected feature vector for age and height and the covariance of control residuals. The score is the covariance-weighted distance from that reference.

Secondary datasets are used only for questions their measurement systems can support. CARE-PD, Mobilise-D, and the Mendeley gait data are not presented as full replications of the frozen eight-input WearGait score when an equivalent measurement bridge is unavailable.

## Interpretation boundaries

This repository does **not** establish:

- diagnosis of Parkinson disease,
- a clinical decision threshold,
- treatment response,
- patient benefit,
- short-term test-retest reliability,
- broad multisite calibration, or
- prospective clinical utility.

The supported claim is narrower: the frozen control-referenced score contains reproducible severity-ranking information beyond gait speed in the primary dataset and can be reconstructed from the audited WearGait walkway records, but it did not meet the prespecified six-plus-month stability standard.

## Repository structure

- `src/` — analysis and validation code
- `scripts/` — reproducible pipeline entry points and acquisition/audit utilities
- `configs/` — frozen analysis configuration
- `results/` — versioned aggregate outputs and figures
- `report/` — evidence tables, bibliography, provenance records, and historical-result index
- `docs/` — preregistration, reproduction guide, and technical notes
- `tests/` — automated checks
- `DATASETS.md` — dataset roles, access boundaries, and supported analyses
- `research_review_parkinsonian_gait.md` — literature context and validation framework

Participant-level records and identifiers are not stored in this public repository.

## Reproduction

Python 3.11 is recommended.

```bash
bash scripts/setup_environment.sh
source .venv/bin/activate
pytest
```

The full analysis requires authorized source datasets outside the repository. Point `PARKINSON_GAIT_DATA_ROOT` to the parent directory containing the authorized dataset folders, then run:

```bash
export PARKINSON_GAIT_DATA_ROOT="/path/to/authorized/Parkinsonian_Gait_Data"
bash scripts/reproduce_final_results.sh
```

The ordered v4.3-v4.5 reconstruction and validation steps are documented in [docs/reproduction_guide.md](docs/reproduction_guide.md). Aggregate evidence and provenance files are indexed in [report/README.md](report/README.md).

## Next experiments

The highest-value next studies are methodological rather than higher-capacity modeling:

1. short-interval repeated walks with task, device, medication timing, and clinical state controlled,
2. MDS-UPDRS gait ratings linked to every repeated gait session to test responsiveness,
3. independent-site validation of the measurement bridge before testing the frozen score,
4. prospective leave-center-out evaluation without refitting on target-site outcomes, and
5. confirmation of ranking, absolute error, and calibration in an independent cohort.

## Research integrity and assistance

The scientific results are versioned separately from presentation files. Automated and computational assistance used in development is documented in [report/AUTHORSHIP_AND_ASSISTANCE.md](report/AUTHORSHIP_AND_ASSISTANCE.md). Competition-ready abstract or report prose is intentionally not stored in this repository; any submitted writing must be prepared and verified independently by the applicant in accordance with the relevant competition rules.
