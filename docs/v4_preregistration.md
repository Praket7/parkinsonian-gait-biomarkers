# v4 prospective biomarker-redesign preregistration

## Question

Can prospectively defined gait phenotypes, designed around documented v3.2.4 failure modes, meet a declared context of use without changing any v3.2.4 result or threshold?

## Locked rules

The original 11 features, v3.2.4 outputs, q <= 0.05, ICC(A,1) >= 0.60, original speed rule, inclusion rules, and quality controls remain unchanged. Every v4 measure is a newly named candidate. No feature definition, threshold, or family may be changed after the protocol manifest is written without a version increment and a post-freeze label.

## Outcome-blind development

Event QC, convergence selection, sensor QC, and control normative fitting do not read clinical severity fields. The static test forbids severity tokens in measurement-development modules. Candidate choice is the closed list in `configs/v4_feature_definitions.yaml`.

## Families and inference

Families are variability rescue, arm/axial, normative deviation, speed response, turning, harmonicity, and Mobilise-D exploratory stability. Each family receives its own BH FDR correction. Clinical associations use participant-clustered GEE with age, height, sex, task, and site where estimable; resampling uses 2,000 participant bootstraps and 5,000 participant permutations. A speed-response construct is not evaluated as speed independent.

## Estimability

An unavailable official signal route, unsupported sensor geometry, insufficient cycles, or insufficient repeated participants is reported as `NOT_ESTIMABLE`, never as a failed or successful biomarker property.
