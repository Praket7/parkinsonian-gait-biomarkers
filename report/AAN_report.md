# Parkinsonian gait biomarkers: aggregate analysis report

Analysis version: `3.1.1`  
Frozen status: `analysis_complete`

## Scope

This report is generated from frozen aggregate outputs. It does not contain
participant identifiers or row-level observations. The primary bundle contains
124 analyzed rows from 62 participants, as reported by the
frozen manifest.

## Main result

Cross-sectional severity association is insufficient for digital-biomarker
qualification: speed independence, context transport, analytical validity,
and repeated-session reliability are separate empirical properties. In the
frozen primary table, 8/11 measures have FDR-adjusted
severity associations. The implemented strict rule identifies
0 candidate trait feature(s): none reported.

Spatial measures must be interpreted after gait-speed adjustment, while
temporal variability can retain association without demonstrating repeatable
measurement. Conversely, repeatable temporal measures need not be the
strongest severity correlates. These statements are derived below from the
frozen association and task-specific reliability tables rather than manually
entered values.

## The central dissociation

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

The primary table also contains Spearman rank and categorical-severity GEE
sensitivities. They are reported to check that treating the ordinal gait item
as a linear trend does not stand alone; they are sensitivities, not additional
confirmatory endpoints.

## Aggregate associations

- `gait_speed`: effect=-0.308, p=0.000114, q=0.000418
- `cadence`: effect=-0.0971, p=0.401, q=0.401
- `step_length_mean`: effect=-0.367, p=5.82e-07, q=3.2e-06
- `stride_length_mean`: effect=-0.375, p=3.31e-07, q=3.2e-06
- `step_time_mean`: effect=0.164, p=0.175, q=0.21
- `stride_time_mean`: effect=0.158, p=0.19, q=0.21
- `step_time_cv`: effect=0.453, p=0.00597, q=0.0135
- `stride_time_cv`: effect=0.347, p=0.0354, q=0.0487
- `stance_fraction`: effect=0.277, p=0.00778, q=0.0135
- `swing_fraction`: effect=-0.277, p=0.00778, q=0.0135
- `double_support_fraction`: effect=0.29, p=0.00858, q=0.0135

## Reliability summary

- `cadence`: status=OK, icc_2_1=0.356
- `cadence`: status=OK, icc_2_1=0.715
- `step_time_mean`: status=OK, icc_2_1=0.411
- `step_time_mean`: status=OK, icc_2_1=0.711
- `step_time_cv`: status=OK, icc_2_1=-0.252
- `step_time_cv`: status=OK, icc_2_1=0.141
- `stride_time_mean`: status=OK, icc_2_1=0.348
- `stride_time_mean`: status=OK, icc_2_1=0.679
- `stride_time_cv`: status=OK, icc_2_1=0.0609
- `stride_time_cv`: status=OK, icc_2_1=0.181

## Feature evidence matrix

- `gait_speed`: aggregate row reported
- `cadence`: aggregate row reported
- `step_length_mean`: aggregate row reported
- `stride_length_mean`: aggregate row reported
- `step_time_mean`: aggregate row reported
- `stride_time_mean`: aggregate row reported
- `step_time_cv`: aggregate row reported
- `stride_time_cv`: aggregate row reported
- `stance_fraction`: aggregate row reported
- `swing_fraction`: aggregate row reported
- `double_support_fraction`: aggregate row reported

## Contact validation

- `cadence`: status=PASS, spearman_rho=0.952, n=189
- `step_time_mean`: status=PASS, spearman_rho=0.949, n=189
- `step_time_cv`: status=FAIL, spearman_rho=0.67, n=189
- `stride_time_mean`: status=PASS, spearman_rho=0.927, n=189
- `stride_time_cv`: status=FAIL, spearman_rho=0.523, n=189

## External translation check

These are cohort-specific translation-speed checks, not full matched-feature
replication. CARE matched temporal replication is included only if the
prespecified canonical event QC can support it; unavailable canonical foot or
ankle events are reported as not estimable, never as a negative replication.

- `3DGait`: status=ok, effect=-0.785, p_value=6.74e-25, ci_low=-0.934, ci_high=-0.636, n_trials=90
- `3DGait`: status=ok, effect=-0.724, p_value=3.81e-15, ci_low=-0.905, ci_high=-0.544, n_trials=90
- `3DGait`: status=ok, effect=-0.77, p_value=2.33e-23, ci_low=-0.922, ci_high=-0.619, n_trials=90
- `BMCLab`: status=ok, effect=-0.688, p_value=1.57e-05, ci_low=-1, ci_high=-0.376, n_trials=781
- `BMCLab`: status=ok, effect=-0.687, p_value=1.49e-05, ci_low=-0.998, ci_high=-0.376, n_trials=781
- `BMCLab`: status=ok, effect=-0.685, p_value=1.67e-05, ci_low=-0.997, ci_high=-0.373, n_trials=781
- `BMCLab`: status=ok, effect=-0.761, p_value=2.1e-06, ci_low=-1.08, ci_high=-0.447, n_trials=371
- `BMCLab`: status=ok, effect=-0.614, p_value=0.00277, ci_low=-1.02, ci_high=-0.212, n_trials=410
- `PD-GaM`: status=ok, effect=-0.748, p_value=1.46e-28, ci_low=-0.88, ci_high=-0.616, n_trials=1.7e+03
- `PD-GaM`: status=ok, effect=-0.759, p_value=5.2e-30, ci_low=-0.89, ci_high=-0.629, n_trials=1.7e+03
- `PD-GaM`: status=ok, effect=-0.762, p_value=1e-26, ci_low=-0.902, ci_high=-0.623, n_trials=1.7e+03
- `T-SDU-PD`: status=ok, effect=-0.461, p_value=7.38e-05, ci_low=-0.688, ci_high=-0.233, n_trials=381
- `T-SDU-PD`: status=ok, effect=-0.455, p_value=2.63e-05, ci_low=-0.667, ci_high=-0.243, n_trials=381
- `T-SDU-PD`: status=ok, effect=-0.477, p_value=2.29e-05, ci_low=-0.697, ci_high=-0.256, n_trials=381
- `3DGait`: status=NOT_ESTIMABLE, n_trials=0
- `3DGait`: status=NOT_ESTIMABLE, n_trials=0
- `3DGait`: status=NOT_ESTIMABLE, n_trials=0
- `3DGait`: status=NOT_ESTIMABLE, n_trials=0
- `BMCLab`: status=NOT_ESTIMABLE, n_trials=0
- `BMCLab`: status=NOT_ESTIMABLE, n_trials=0
- `BMCLab`: status=NOT_ESTIMABLE, n_trials=0
- `BMCLab`: status=NOT_ESTIMABLE, n_trials=0
- `PD-GaM`: status=NOT_ESTIMABLE, n_trials=0
- `PD-GaM`: status=NOT_ESTIMABLE, n_trials=0
- `PD-GaM`: status=NOT_ESTIMABLE, n_trials=0
- `PD-GaM`: status=NOT_ESTIMABLE, n_trials=0
- `T-SDU-PD`: status=NOT_ESTIMABLE, n_trials=0
- `T-SDU-PD`: status=NOT_ESTIMABLE, n_trials=0
- `T-SDU-PD`: status=NOT_ESTIMABLE, n_trials=0
- `T-SDU-PD`: status=NOT_ESTIMABLE, n_trials=0

## Medication-state sensitivity

- `gait_speed`: status=OK, effect=-0.318, p_value=0.000286
- `cadence`: status=OK, effect=-0.0764, p_value=0.553
- `step_length_mean`: status=OK, effect=-0.388, p_value=4.66e-07
- `stride_length_mean`: status=OK, effect=-0.397, p_value=3.18e-07
- `step_time_mean`: status=OK, effect=0.158, p_value=0.225
- `stride_time_mean`: status=OK, effect=0.151, p_value=0.249
- `step_time_cv`: status=OK, effect=0.445, p_value=0.00527
- `stride_time_cv`: status=OK, effect=0.334, p_value=0.0416
- `stance_fraction`: status=OK, effect=0.247, p_value=0.037
- `swing_fraction`: status=OK, effect=-0.247, p_value=0.037
- `double_support_fraction`: status=OK, effect=0.264, p_value=0.0343

## Negative controls

- `gaussian_feature`: status=OK, effect=0.0989, p_value=0.245
- `shuffled_severity`: status=OK, effect=0.0254, p_value=0.764
- `site_only_severity`: status=OK, p_value=0.373

## Limitations and deviations

- Reference PKMAS measures are valid reference outcomes, not failed proxies.
- V2 archive filename/header/schema audit found no joinable session-level clinical-score table, so clinical change was not fitted.
- CARE-PD is a cohort-specific limited translation check; matched temporal replication is included only if event QC passes.

Do not interpret this report as diagnostic, causal, treatment, or clinical-use
evidence. Regenerate it after every authorized analysis run.
