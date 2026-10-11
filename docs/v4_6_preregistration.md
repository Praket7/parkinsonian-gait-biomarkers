# v4.6 preregistration

## Status

This document freezes the v4.6 biomarker failure-mode extension before any v4.6 scientific result is produced. v4.6 does not alter the frozen v4.1 score or revise historical v4.3 through v4.5 findings. The v4.5 conclusion that the score failed its prespecified six-plus-month longitudinal stability criterion remains historical truth regardless of v4.6 outcomes.

Row-level authorized WearGait derivatives are intentionally not stored in the public repository. The scientific runners therefore accept controlled local inputs. Continuous integration uses synthetic fixtures to verify algorithms, contracts, determinism, and claim boundaries. A real-data v4.6 result may be released only after the frozen protocol check passes in the controlled analysis environment.

## Research questions

1. Does the final frozen composite score agree when calculated from PKMAS gait features versus independently reconstructed raw-walkway features?
2. Across visits separated by at least six months, is each participant's multivariate direction of healthy-reference gait deviation conserved more than expected under random cross-person pairing?
3. Does uncertainty in which healthy participants define the reference materially change the six-plus-month scalar stability or deviation-direction findings?

No external cohort is analyzed in v4.6.

## Frozen score and residual geometry

For participant or visit i, the frozen healthy reference predicts the eight-feature gait vector from age and height. Let

`r_i = x_i - mu_control(age_i, height_i)`

and let `P = pinv(Sigma)` for the frozen healthy residual covariance matrix. The historical score remains

`D_i = sqrt(r_i.T @ P @ r_i)`.

No Parkinson severity outcome may enter feature selection, healthy-reference fitting, covariance fitting, feature weighting, threshold selection, or any v4.6 score definition.

The primary direction statistic between visits is the precision-metric cosine

`C_P(a,b) = (a.T @ P @ b) / sqrt((a.T @ P @ a) * (b.T @ P @ b))`.

Cosines are clipped to [-1, 1] only for floating-point safety before conversion to angles. A residual with zero or numerically degenerate precision-metric magnitude is excluded from direction inference and counted. It is never coerced to zero similarity.

## Question 1. Final-score analytical agreement

For every available matched V1 trial, the exact same frozen model and age/height covariates are used to score the PKMAS feature vector and the independently reconstructed raw-walkway feature vector. Length and speed units are converted identically before scoring.

Primary agreement summaries are ICC(A,1), Lin concordance correlation coefficient, mean bias, mean absolute error, root mean squared error, and Bland-Altman limits of agreement. Pearson and Spearman correlations are secondary because correlation alone does not establish agreement. No new binary clinical qualification threshold is introduced for the final score.

The scale of PKMAS-versus-reconstruction score disagreement will be compared descriptively with the historical six-plus-month absolute score-change scale. This comparison is descriptive and will not be converted into a significance test whose purpose is to declare analytical error negligible.

## Question 2. Longitudinal deviation-pattern conservation

SelfPace and HurriedPace are analyzed separately. The longitudinal endpoint remains the historical four-valid-pass featurewise median followed by the unchanged frozen score transformation. Participant/session/task duplicates are invalid. Only participants with both sessions for a task enter its paired analysis.

The primary task statistic is the median within-person precision-metric cosine. Sampling uncertainty is estimated using 2,000 participant-level bootstrap resamples and percentile 95 percent intervals.

The null distribution uses 10,000 within-task permutations. Session 1 participant order is fixed and session 2 participant assignments are permuted. The one-sided p value tests whether observed median within-person similarity is greater than random cross-person pairing and uses the plus-one correction

`p = (1 + count(null >= observed)) / (1 + n_permutations)`.

Exactly the two primary task p values are adjusted with the Holm method. Directional similarity is described as pattern conservation or directional stability. It is not called test-retest reliability.

## Question 3. Healthy-reference uncertainty

Healthy controls are resampled by participant with replacement 2,000 times. All rows belonging to a sampled control participant remain together and duplicate draws receive unique synthetic bootstrap identifiers before fitting. The reference is fit using controls only with the prespecified sample covariance method.

Within a reference-bootstrap iteration, the same fitted reference is applied to both longitudinal sessions for every participant. For each task and reference resample, the analysis stores ICC(A,1), median within-person precision cosine, mean paired score change, and median paired score change.

Percentiles across these 2,000 reference fits quantify healthy-reference estimation uncertainty. They are not participant-sampling confidence intervals. The historical participant-bootstrap uncertainty from v4.5 remains the sampling uncertainty for the original stability estimate.

An exploratory participant-level table may summarize how each paired score change varies across healthy-reference resamples. Those intervals are not clinically meaningful change thresholds.

## Fixed computational choices

- protocol version: v4.6.0
- random seed: 20261010
- participant bootstrap iterations: 2,000
- healthy-reference bootstrap iterations: 2,000
- direction permutations: 10,000
- primary direction statistic: median
- multiplicity method: Holm across SelfPace and HurriedPace only
- required valid passes per longitudinal session: four
- healthy covariance method: sample covariance with the same regularization already implemented by v4.1
- zero residual rule: exclude and count

These values are mirrored in `configs/v4_6_analysis.yaml` and may not be changed after protocol freeze in response to results.

## Protected historical inputs

At minimum, the v4.6 freeze protects the bytes of

- `results/v4_1/frozen/v4_1_control_model.json`
- `src/v4_1/normative.py`
- `results/v4_3/v1_reconstruction_agreement.csv`
- `results/v4_3/v1_reconstruction_qc.json`
- `results/v4_5/h4b_endpoint_error_corrected.csv`
- `results/v4_5/AAN_v4_5_report.md`

## Interpretation rules fixed before results

A favorable final-score analytical result supports endpoint-level analytical agreement. It does not establish clinical validity or cross-device transport.

Greater within-person direction similarity than random pairing supports conservation of the multivariate abnormality pattern across the long interval. It does not establish short-term reliability, disease progression tracking, responsiveness, or diagnosis. A null direction result means the long-interval instability extends to the multivariate pattern under this analysis.

Low variation across healthy-reference resamples argues against reference sampling as the main explanation for the historical stability result. High variation means healthy-reference estimation materially affects the conclusion. Neither outcome may be used to rewrite v4.5.

If final-score analytical agreement is weak, analytical propagation becomes a plausible contributor and must be addressed before stronger longitudinal interpretation. If it is strong while scalar and directional stability are weak and reference sensitivity is low, the evidence instead points to instability of the observed phenotype across the long interval under uncontrolled clinical states.

Unfavorable and null results remain part of the release. No analysis may be redesigned after seeing results solely to create a favorable finding.

## Claims that remain outside v4.6

v4.6 does not establish diagnosis, disease-progression tracking, treatment response, clinical utility, short-term state-controlled test-retest reliability, clinically meaningful change thresholds, independent full-score transport, or general multi-site validation.
