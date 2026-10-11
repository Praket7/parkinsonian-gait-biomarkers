# v4.6 Biomarker Failure-Mode Design Specification

## Purpose

v4.6 is a prospective extension of the existing Parkinsonian gait biomarker project. It does not revise the frozen v4.1 score, the v4.3 analytical bridge, the v4.5 longitudinal interpretation, or any previously reported result. Its purpose is to answer a narrower and more scientifically useful question:

> When a fixed healthy-reference gait score shows a strong cross-sectional severity relationship but fails a six-plus-month stability criterion, which part of the evidence chain is actually unstable?

The extension uses only the existing authorized WearGait-derived data and artifacts already required by the repository. No new external cohort is used in v4.6.

The scientific objective is not to improve prediction accuracy. It is to decompose failure modes while preserving the project’s strongest design feature: the primary gait score was defined without Parkinson severity outcomes.

## Why this extension is worth doing

The current project already establishes several distinct facts:

1. The fixed eight-input healthy-reference score is associated with gait-specific Parkinsonian severity.
2. The association remains after adjustment for walking speed.
3. The association is robust to 2,000 healthy-reference resamples.
4. The score improves participant-level severity ranking beyond walking speed in repeated grouped validation.
5. All eight inputs can be reconstructed from raw walkway data with strong agreement against PKMAS exports across 252 matched trials.
6. The unchanged score fails the prespecified six-plus-month stability criterion.
7. Short-term state-controlled repeatability, clinical responsiveness, and full multi-site score transport remain unestablished.

The unresolved issue is that these findings live at different levels of the validation chain. A failed long-interval ICC does not tell us whether the failure comes from the final score’s analytical derivation, from sensitivity to which healthy participants define the reference, from a change in the *amount* of gait abnormality, or from a change in the *pattern* of gait abnormality.

Recent digital-measurement literature supports treating these as separate questions. The V3 framework separates verification, analytical validation, and clinical validation. Parkinson-specific work likewise shows that reliability, longitudinal stability, treatment responsiveness, progression tracking, and criterion validity can diverge rather than moving together. Normative-modeling research further argues that the full individual deviation profile can contain information that a single scalar burden score discards.

v4.6 therefore treats the negative long-interval result as a starting point for mechanistic analysis rather than as a result to be optimized away.

## Existing frozen scientific object

Let the frozen v4.1 reference model provide an expected healthy gait vector conditional on age and height,

\[
\mu_i = \mu_{\mathrm{control}}(\mathrm{age}_i,\mathrm{height}_i),
\]

and a healthy residual covariance matrix

\[
\Sigma.
\]

For an observed eight-feature gait vector \(x_i\), define the healthy-reference residual

\[
r_i = x_i - \mu_i.
\]

The current scalar score is

\[
D_i = \sqrt{r_i^T P r_i},
\]

where

\[
P = \Sigma^{+}
\]

is the Moore-Penrose inverse of the frozen covariance matrix. This definition must remain unchanged.

The eight frozen inputs remain:

1. gait speed
2. cadence
3. mean step length
4. mean stride length
5. mean step time
6. mean stride time
7. step-time coefficient of variation
8. stride-time coefficient of variation

No Parkinson outcome is permitted to alter the feature set, coefficient estimates, covariance matrix, score definition, or thresholds in this extension.

---

# Core contribution 1: Final-score analytical agreement

## Question

The current analytical bridge validates each of the eight inputs separately. Does the *final composite score itself* remain analytically consistent when calculated from PKMAS-exported inputs versus independently reconstructed raw-walkway inputs?

This is not redundant with v4.3. A nonlinear multivariate function can amplify or cancel feature-level differences, so strong agreement of all inputs does not mathematically guarantee strong agreement of the final derived endpoint.

## Dataset

Use the existing 252 matched v4.3 V1 trials already represented in:

- `results/v4_3/v1_reconstructed_features.csv`
- the corresponding V1 clinical covariates
- the SHA256-checked frozen v4.1 reference model

No new source data are introduced.

## Analysis

For every matched trial, construct two otherwise identical rows:

- one from PKMAS feature values
- one from raw-reconstructed feature values

Apply the same unit conversions, age, height, frozen conditional mean, and frozen covariance to both.

Calculate:

\[
D_{\mathrm{PKMAS}}
\]

and

\[
D_{\mathrm{raw}}.
\]

Primary agreement outputs:

- ICC(A,1) absolute agreement
- Lin concordance correlation coefficient
- mean bias
- MAE
- RMSE
- Bland-Altman 95% limits of agreement

Secondary descriptive outputs:

- Pearson correlation
- Spearman correlation
- relative bias when interpretable

## Interpretation rule

Correlation alone must never be described as analytical agreement. A high Pearson or Spearman coefficient can coexist with unacceptable systematic bias.

Because there is no independently established clinically meaningful error margin for this new composite score, v4.6 must not invent a regulatory or clinical equivalence threshold after looking at the results. The existing `>=0.90` feature-level ICC/CCC benchmark can be reported as a sensitivity benchmark, but the primary interpretation must use the complete agreement profile, especially absolute bias and limits of agreement.

## Link to longitudinal failure

Compare the distribution of absolute PKMAS-versus-raw score differences with the distribution of observed six-plus-month within-participant score differences.

This comparison is descriptive only. It may support a statement such as:

> Raw-reconstruction disagreement was much smaller than the observed long-interval score changes.

It must not support a statement such as:

> Measurement error was ruled out.

The analytical bridge does not capture biological state fluctuation, visit-to-visit setup effects, medication state, disease change, or every other source of measurement variation.

---

# Core contribution 2: Longitudinal deviation geometry

## Scientific motivation

The current scalar score answers:

> How far is this gait pattern from the fitted healthy reference?

It does not answer:

> In what *direction* is the gait pattern abnormal?

Two people can have the same scalar distance from normal while differing completely in whether their abnormality is dominated by pace, rhythm, or variability. The same person can also preserve the composition of abnormality while the total magnitude changes.

Normative-modeling work increasingly treats individualized deviation profiles as scientific objects rather than reducing them immediately to a global burden value. v4.6 adapts that principle without changing the frozen healthy-reference model.

## Primary representation

Keep the original residual vector \(r_i\). The same precision matrix used by the frozen score defines the geometry.

For two residual vectors \(r_a\) and \(r_b\), define precision-metric cosine similarity:

\[
C_P(r_a,r_b) =
\frac{r_a^T P r_b}
{\sqrt{r_a^T P r_a}\sqrt{r_b^T P r_b}}.
\]

Properties:

- \(+1\) means identical deviation direction up to positive scaling.
- \(0\) means orthogonal deviation patterns in the frozen healthy-reference geometry.
- \(-1\) means opposite deviation directions.
- It is invariant to positive scalar multiplication of either residual vector.
- The denominator contains the same quadratic forms used by the frozen scalar score.

This can also be viewed as ordinary cosine similarity after whitening by the healthy covariance. The implementation should use the precision-form expression directly so the result is not dependent on an arbitrary choice of covariance square root.

The term `precision-metric cosine` should be used in repository outputs. Avoid reusing the term `Mahalanobis cosine similarity` without qualification because some machine-learning literature applies covariance weighting to dual-space directions, whereas this project compares primal-space residual vectors using inverse covariance.

## Primary longitudinal test

For each task separately:

- SelfPace
- HurriedPace

pair session 1 and session 2 for the same participant using the same inclusion rules as the corrected v4.5 endpoint.

Compute each participant’s within-person precision-metric cosine.

The primary statistic is the median within-person similarity for the task.

### Null comparison

Generate 10,000 deterministic permutations of session-2 participant labels within each task while keeping session-1 rows fixed. For each permutation, calculate the median mismatched-person similarity.

The one-sided primary hypothesis is:

> The median within-person directional similarity is greater than expected from random cross-person pairing.

Calculate the permutation p-value as

\[
p = \frac{1 + \#(T_{\mathrm{null}} \ge T_{\mathrm{observed}})}{1 + N_{\mathrm{perm}}}.
\]

Correct the two primary task p-values using Holm correction.

### Sampling uncertainty

Bootstrap participants within each task with 2,000 fixed-seed resamples to estimate a percentile 95% confidence interval for the median within-person similarity.

The participant bootstrap and the permutation null answer different questions and must remain separate.

## Secondary geometry outputs

Report:

- angular change \(\arccos(C_P)\), in radians and degrees
- distribution of featurewise signed standardized/whitened contributions for descriptive visualization
- pace, rhythm, and variability group contributions, descriptive only
- absolute change in scalar magnitude \(|D_2-D_1|\)
- relationship between angular change and magnitude change as a descriptive Spearman statistic

No feature-level association with Parkinson outcomes is used to choose or weight these components.

## Interpretation matrix

### Scalar magnitude unstable, direction conserved

Potential interpretation:

> The amount of gait deviation changes across long intervals, while the multivariate composition of abnormality remains more individually conserved than expected by chance.

This would support the idea that a one-number biomarker discards potentially persistent phenotypic structure.

### Scalar magnitude unstable, direction not conserved

Potential interpretation:

> Long-interval instability extends to the multivariate gait phenotype itself rather than being confined to global score magnitude.

This is also scientifically informative.

### Task-specific conservation

If one task shows conservation and the other does not, report task dependence directly. Do not pool tasks to manufacture a stronger result.

## Prohibited interpretation

Directional conservation is not short-term reliability, progression sensitivity, medication response, diagnostic accuracy, or proof of a stable biological trait. Visits remain separated by at least six months and lack verified matched clinical state anchors.

---

# Core contribution 3: Healthy-reference uncertainty propagated into longitudinal conclusions

## Question

The v4.1 bootstrap showed that the *cross-sectional association* retained the same direction across 2,000 resampled healthy references. But does the *longitudinal failure* also persist when the healthy reference itself is perturbed?

This separates two sources of uncertainty:

- uncertainty from which healthy participants define normal
- uncertainty from which Parkinson participants happen to be observed

The current project evaluates the second through participant bootstrap confidence intervals on the ICC. v4.6 adds the first explicitly.

## Bootstrap design

Use the same participant-level control resampling concept and deterministic seed family as the frozen v4.1 analysis.

For each of 2,000 healthy-reference bootstrap iterations:

1. Sample healthy participants with replacement.
2. Preserve all rows belonging to each sampled participant.
3. Refit the healthy age/height conditional mean and residual covariance using controls only.
4. Score both longitudinal sessions using the *same bootstrap reference*.
5. Compute SelfPace and HurriedPace ICC(A,1) point estimates.
6. Compute task-level median precision-metric cosine using the bootstrap precision matrix.
7. Retain participant-level paired score differences for reference-uncertainty summaries.

Parkinson outcomes must not enter the reference-fitting process.

## Primary outputs

For each task report the distribution across healthy-reference bootstraps of:

- ICC(A,1) point estimate
- median directional similarity
- mean/median session-2 minus session-1 score change

Summarize each by:

- median
- 2.5th percentile
- 97.5th percentile
- fraction of bootstrap references with ICC point estimate at or above 0.80

The last quantity is a robustness descriptor, not a confidence interval and not a replacement for the original participant-bootstrap lower-bound criterion.

## Individual reference uncertainty

For each deidentified participant and task, summarize the 2,000 paired score changes across reference bootstraps:

- original-reference change
- bootstrap median change
- 2.5th and 97.5th percentiles
- fraction of references in which the sign agrees with the original-reference change

These are exploratory individualized uncertainty summaries. They must not be interpreted as clinical change thresholds.

## Critical statistical separation

The following quantities must not be conflated:

- participant bootstrap CI: uncertainty from the sampled Parkinson participants
- healthy-reference bootstrap spread: uncertainty from the sampled control reference
- six-plus-month within-person change: mixture of clinical change, state differences, and measurement variation
- within-session pass resampling: conditional technical precision given the observed passes

v4.6 should make these distinctions visually explicit.

---

# What v4.6 deliberately does not do

## No new prediction model

No random forest, XGBoost, neural network, supervised latent score, or outcome-driven feature selection is added. The sample is not large enough to justify making higher model capacity the scientific contribution, and doing so would weaken the outcome-blind design.

## No external cohort

External transport is deferred until an independent dataset is intentionally acquired and audited for measurement compatibility.

## No claim of responsiveness

There is no verified session-matched repeated MDS-UPDRS and medication-state anchor in the current longitudinal source. Clinical responsiveness remains not estimable.

## No short-term reliability claim

The longitudinal visits are at least six months apart. v4.6 continues to label the result as long-interval or six-plus-month stability.

## No post-hoc threshold optimization

New pass/fail thresholds may not be selected after results are observed. Where no defensible threshold already exists, report estimates, uncertainty, and comparison distributions instead of manufacturing a binary success criterion.

## No headline adaptability biomarker in v4.6

The repository already contains univariate SelfPace-to-HurriedPace scaling indices. A new multivariate healthy-referenced adaptability measure could be scientifically interesting, but it should be a separately frozen extension because it introduces a new measurement object and additional researcher degrees of freedom. It is therefore deferred to a possible v4.7 after v4.6 is frozen.

---

# Research basis

The design is motivated by five converging lines of work.

## 1. Validation layers are distinct

Goldsack and colleagues’ V3 framework separates verification, analytical validation, and clinical validation for biometric monitoring technologies. This supports validating the final derived measurement separately from asking whether it is clinically meaningful.

Reference: Goldsack JC et al. *Verification, analytical validation, and clinical validation (V3): the foundation of determining fit-for-purpose for Biometric Monitoring Technologies.* npj Digital Medicine. 2020. https://doi.org/10.1038/s41746-020-0260-4

Ellis and colleagues provide a Parkinson-relevant implementation of stepwise verification and analytical validation and use absolute-agreement ICC, MAE, RMSE, and related error measures according to the measurement task.

Reference: Ellis R et al. *Sensor Verification and Analytical Validation of Algorithms to Measure Gait and Balance and Pronation/Supination in Healthy Volunteers.* Sensors. 2022. https://doi.org/10.3390/s22166275

## 2. Correlation is not longitudinal qualification

Far and colleagues directly separate test-retest reliability, longitudinal stability, disease-control differentiation, and medication sensitivity in Parkinson digital measures.

Reference: Far MS et al. *Exploring Test-Retest Reliability and Longitudinal Stability of Digital Biomarkers for Parkinson Disease in the m-Power Data Set.* JMIR. 2021. https://doi.org/10.2196/26608

A systematic review of progression biomarkers concluded that digital outcomes remain promising but their ability to track Parkinson progression is not yet established consistently.

Reference: Rábano-Suárez P et al. *Digital Outcomes as Biomarkers of Disease Progression in Early Parkinson's Disease: A Systematic Review.* Movement Disorders. 2024. https://doi.org/10.1002/mds.30056

## 3. Context of use matters

Recent Parkinson gait reviews emphasize that gait variables may behave differently for susceptibility, progression, treatment response, and prognosis. The same statistically strong measure should not be assumed to serve all purposes.

Reference: Mancini M et al. *Digital gait biomarkers in Parkinson’s disease: susceptibility/risk, progression, response to exercise, and prognosis.* npj Parkinson's Disease. 2025. https://www.nature.com/articles/s41531-025-00897-1

## 4. Individual deviation profiles can matter beyond global burden

Normative modeling treats a healthy reference as a coordinate system for individualized deviations and is specifically intended to preserve heterogeneity that group averages or global summaries can obscure.

Reference: Marquand-style normative modeling framework review. https://pmc.ncbi.nlm.nih.gov/articles/PMC7613648/

Longitudinal normative-modeling work introduces explicit measures of within-person change relative to a population standard rather than assuming a cross-sectional deviation is itself a longitudinal endpoint.

Reference: Bučková B et al. *Using normative models pre-trained on cross-sectional data to evaluate intra-individual longitudinal changes in neuroimaging data.* eLife. 2025. https://elifesciences.org/articles/95823

Recent computational work also argues that an individualized deviation map can itself be the inferential target rather than merely an intermediate residual summary. This is methodological inspiration rather than Parkinson-specific clinical evidence.

Reference: Korley JT. *A Bayesian Longitudinal Spatial Normative Model for Individualized Brain Deviation Mapping.* arXiv:2605.14565. https://arxiv.org/abs/2605.14565

## 5. Non-Euclidean direction similarity should respect covariance geometry

A recent computational paper formalizes covariance-aware cosine measures and shows why Euclidean angles can be misleading in correlated feature spaces. Its exact dual-space metric is not copied here; it motivates using the same frozen precision geometry already encoded in the Parkinson gait score when comparing primal-space residual directions.

Reference: Ying ZJ, Hase P, Kriegeskorte N. *Comparing Linear Probes with Mahalanobis Cosine Similarity.* arXiv:2606.19603. https://arxiv.org/abs/2606.19603

---

# Planned v4.6 outputs

The extension should produce at minimum:

- `results/v4_6/score_level_analytical_agreement.csv`
- `results/v4_6/deviation_direction_pairs.csv`
- `results/v4_6/deviation_direction_summary.csv`
- `results/v4_6/deviation_direction_null.csv`
- `results/v4_6/reference_uncertainty_longitudinal.csv`
- `results/v4_6/reference_uncertainty_individual.csv`
- `results/v4_6/failure_mode_summary.json`
- `results/v4_6/v4_6_report.md`
- a small set of publication-quality figures in `results/v4_6/figures/`

Participant-level outputs must remain deidentified and contain no direct personal identifiers.

---

# Success criteria for the extension itself

v4.6 is considered scientifically successful if it answers the prespecified failure-mode questions clearly, even if every new result is negative.

It must be possible to state, without post-hoc reinterpretation:

1. whether the final score is analytically preserved across PKMAS and raw reconstruction,
2. whether within-person gait-deviation direction is more conserved than random cross-person pairing,
3. whether the long-interval stability conclusion materially depends on which healthy participants define the normative reference.

A null result on any of these questions is acceptable. The extension is designed to reduce uncertainty, not to guarantee a more favorable biomarker result.

## Claim boundary after v4.6

Even a favorable v4.6 cannot establish:

- diagnosis
- disease progression tracking
- treatment response
- short-term test-retest reliability
- clinical utility
- general multi-site transportability
- a clinically meaningful change threshold

Those remain separate evidence requirements.
