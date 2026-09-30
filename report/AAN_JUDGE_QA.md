# Questions a judge may ask

## Why only 62 participants in the main severity analysis?

The main WearGait screen contains 62 independent people and 124 task observations. Repeating tasks gives more measurements, not more independent participants. The score association table records 125 analyzed rows from those same 62 people. Models cluster by participant, and every held-out split keeps each participant's records together. This is still a modest clinical sample, so estimates and subgroup conclusions need cautious interpretation.

## Why not use deep learning?

The central question is whether a fixed gait measure survives distinct validation tests. A high-capacity model would make attribution harder and is not justified by 62 independent participants. The project therefore keeps the score low-dimensional and frozen, and uses grouping to prevent a person's records from appearing in both training and test folds.

## Why compare against gait speed?

Gait speed is a familiar, strong summary of walking performance. Testing the deviation score against speed asks whether it contributes ordering information beyond that baseline. The result supports improved ranking, not consistently better exact clinical-score prediction.

## Why did the longitudinal test fail?

The prespecified rule required the lower confidence bound for the score's ICC to reach 0.80. The corrected four-pass endpoint estimates did not meet that rule for either task. However, visits were at least six months apart. Disease progression and medication or health-state changes may contribute to score differences, so this is a failure of six-plus-month stability under changing conditions, not a failed short-term test-retest experiment.

## Is a failed validation layer bad for the project?

It is a negative scientific result. The purpose was to test qualification criteria without relaxing them after seeing the data. The association and measurement bridge remain supported, while long-interval stability failed. Keeping both findings is more informative than calling every positive association a biomarker.

## Why is CARE-PD not a full replication?

CARE-PD supplies heterogeneous anonymized motion records and gait labels, but it does not provide a validated mapping to every frozen PKMAS walkway input and the same healthy reference. Translation-speed analyses are reported separately. They are not relabeled as replication of the eight-input score.

## What is actually new here?

The contribution is the prespecified validation architecture applied to a control-referenced score. It separates association, healthy-reference robustness, incremental ranking, analytical agreement, longitudinal stability, responsiveness, and transport. The project does not claim that gait features or multivariate scores were invented here.

## Can this diagnose Parkinson's disease?

No. The study relates gait measurements to a concurrent gait-specific clinical rating in people already enrolled in the source study. It did not test a diagnostic decision, clinical threshold, or prospective patient-care workflow.

## Can it monitor treatment?

That has not been established. Medication labels or timing in secondary datasets do not substitute for a validated measurement bridge and linked repeated clinical anchors.

## What experiment should come next?

A short-interval repeated-walk study should hold task, equipment, clinical state, and medication timing as constant as possible. It should collect MDS-UPDRS gait ratings at every visit. The frozen score should then be evaluated at an independent site, with the same measurement bridge validated before any score comparison.

## Why does the paper separate ranking from prediction?

Spearman correlation evaluates whether people are ordered similarly. RMSE and MAE evaluate the numerical distance between predicted and observed scores. The repeated validation strongly favors rank ordering, while absolute-error metrics do not show a consistent advantage. Those are different claims.
