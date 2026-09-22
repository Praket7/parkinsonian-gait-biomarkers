# Parkinsonian gait biomarkers: evidence report

Analysis protocol version: `3.2.4`  
Release version: `v3.2.4`  
Frozen status: `analysis_complete`

> **Current-release note (v4.4.0):** This report preserves the frozen v3.2.4
> primary analysis. The subsequent raw-walkway and measurement-protocol
> closures are reported separately in [v4.3 H4 reconstruction](../docs/v4_3_h4_reconstruction.md)
> and the [v4.4 evidence report](../results/v4_4/AAN_v4_4_report.md). The
> current conclusion remains that no gait feature or composite is qualified as
> a stable context-robust trait biomarker under the strict criteria.

## Question and scope

This report is generated from frozen aggregate outputs. It does not contain
participant identifiers or row-level observations. The primary bundle contains
124 analyzed rows from 62 participants, as reported by the
frozen manifest.

Can a gait feature be called a context-robust Parkinsonian trait biomarker
rather than merely a cross-sectional correlate? We predeclared that the answer
requires convergent evidence for severity association, speed independence where
relevant, context behavior, analytical validity, and repeatability. This
fit-for-purpose framing follows established biomarker-validation guidance
([2](AAN_bibliography.md#bibliography)) and avoids treating one statistically
significant coefficient as qualification.

## Main finding

Cross-sectional severity association is insufficient for digital-biomarker
qualification: speed independence, context transport, analytical validity,
and repeated-session reliability are separate empirical properties. In the
frozen primary table, 8/11 measures have FDR-adjusted
severity associations. The implemented strict rule identifies 0
candidate trait feature(s): none reported.

Spatial measures must be interpreted after gait-speed adjustment, while
temporal variability can retain association without demonstrating repeatable
measurement. Conversely, repeatable temporal measures need not be the
strongest severity correlates. These statements are derived below from the
frozen association and task-specific reliability tables rather than manually
entered values.

## Why the result matters

The practical result is a three-way separation, not a ranking of coefficients.
First, gait speed declines by -0.151 m/s per one-point higher
gait-item score in the adjusted cross-sectional model. Second, step length
declines by -0.0674 m per point, but the speed-adjusted
step- and stride-length q-values do not meet the declared threshold; their
primary association therefore cannot be interpreted as speed-independent.
Third, step-time variability increases by 1.84 percentage points
per point and retains its speed-adjusted association, yet its SP repeated-session
ICC is below the candidate threshold. This is the project’s core observation:
severity sensitivity, speed independence, and repeatability are empirically
distinct properties.

| Evidence question | Prespecified result | Interpretation |
| --- | --- | --- |
| Severity association | 8/11 FDR-significant | Association is not qualification. |
| Spatial independence | Step- and stride-length speed-adjusted q-values miss the threshold | Raw association is plausibly speed-mediated. |
| Temporal independence | Step-time CV remains speed-adjusted | It is not automatically a trait measure. |
| Repeatability | Step-time CV SP ICC(A,1) = 0.141 | It fails the repeatability requirement. |
| Strict conclusion | 0 qualifying features | No context-robust trait feature was identified. |

The primary table also contains Spearman rank and categorical-severity GEE
sensitivities. They are reported to check that treating the ordinal gait item
as a linear trend does not stand alone; they are sensitivities, not additional
confirmatory endpoints.

## Translation check

CARE-PD contributes a limited, cohort-specific reconstructed-motion check:
endpoint forward-translation speed is negatively associated with severity in
each analyzed cohort (3DGait -0.785 (n=43); BMCLab -0.688 (n=23); PD-GaM -0.748 (n=30); T-SDU-PD -0.461 (n=14)). These are translation-speed associations,
not pooled evidence and not matched-feature replication.

The acquired CARE-PD release contains canonical SMPL records but no official
H36M-preprocessed assets in its accessible file listing. The prespecified
matched features are therefore **not estimable**, never a negative replication
and never an improvised SMPL conversion. This boundary follows the CARE-PD
release and code documentation ([5](AAN_bibliography.md#bibliography)).

## Interpretation for judges

## Independent external evidence

Mobilise-D contributes repeated real-world broad-motor-anchor evidence: walking speed and stride length meet the frozen four-feature FDR criterion, whereas cadence and stride duration do not. Mendeley supplies independent processed-table transport evidence. These contexts do not alter the original WearGait trait decision.

- `gait_speed`: status=OK, p_value=0.00228, q_value=0.00455, ci_low=-0.00111, ci_high=-0.000243
- `stride_length_mean`: status=OK, p_value=0.000427, q_value=0.00171, ci_low=-0.00106, ci_high=-0.000302
- `cadence`: status=OK, p_value=0.408, q_value=0.544, ci_low=-0.0383, ci_high=0.0156
- `stride_time_mean`: status=OK, p_value=0.674, q_value=0.674, ci_low=-0.000277, ci_high=0.000429
- `stride_amplitude_cm`: status=OK, spearman_rho=-0.617, n=42
- `stride_amplitude_sd_cm`: status=OK, spearman_rho=-0.00944, n=42
- `gait_speed_m_s`: status=OK, spearman_rho=-0.656, n=42
- `stride_speed_sd`: status=OK, spearman_rho=-0.0719, n=42
- `speed_correlation`: status=OK, spearman_rho=-0.228, n=42
- `foot_lift_cm`: status=OK, spearman_rho=-0.373, n=42
- `foot_lift_sd_cm`: status=OK, spearman_rho=-0.314, n=42
- `arm_swing_indicator`: status=OK, spearman_rho=-0.761, n=42

The high-value outcome is a rigorous negative qualification result. It narrows
an initially plausible candidate: step-time variability survives speed
adjustment but does not survive the repeatability requirement. That conclusion
is stronger than a coefficient leaderboard because it specifies what must be
true before a wearable gait signal could be defended as a stable trait measure.
The project also separates what was measured, what translated across an
external dataset, and what was not estimable because required official assets
were unavailable.

## Reproducibility and audit trail

All displayed values are generated from identifier-free frozen aggregates.
Feature-level estimates, task reliability, contact agreement, medication
sensitivity, negative controls, CARE cohort results, and the strict evidence
matrix are retained in the accompanying appendix and CSV files. The protocol
version is intentionally separate from the packaging release version so a
release update cannot silently alter the analysis specification. The
claim-to-evidence map is in [claim_evidence_matrix.csv](claim_evidence_matrix.csv),
and sources are in [AAN_bibliography.md](AAN_bibliography.md).

## Limitations

- Reference PKMAS measures are valid reference outcomes, not failed proxies.
- V2 archive filename/header/schema audit found no joinable session-level clinical-score table, so clinical change was not fitted.
- CARE-PD is a cohort-specific limited translation check; matched temporal replication is included only if event QC passes.

Do not interpret this report as diagnostic, causal, treatment, or clinical-use
evidence. Regenerate it after every authorized analysis run.
