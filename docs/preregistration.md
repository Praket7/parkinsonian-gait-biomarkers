# Analysis freeze v2

This repository implements the pre-specified, interpretable feature layer for
secondary analysis of de-identified movement datasets. The primary unit is a
participant-task (with repeated sessions retained as metadata), and the
primary tasks are SP, HP, SPm, and HPm. The released V1 PKMAS reference table
contains SP and HP only, so the reference primary analysis is restricted to
those two tasks; SPm/HPm are contact-signal context checks. Straight walking is
defined by the release's `Walk` annotations and is split at gaps over 2 s.

No participant-level split may place the same participant in both train and
test. External data are never used to tune thresholds. Features are reported
with effect sizes and uncertainty, and multiple testing is corrected before
calling a trait marker. A statistical association is not interpreted as
causal or as a clinical diagnosis.

The primary model is participant-clustered GEE adjusted for age, height, sex,
task, and site. The trait conjunction is q<=0.05, whole-participant bootstrap
direction consistency >=0.80, validated contact agreement rho>=0.70 when a
contact proxy is used, and longitudinal ICC(2,1)>=0.60. CARE-PD is a held-out,
translation-only directional check after canonical forward-axis and 0.2-3.0
m/s plausibility QC. The frozen configuration is `configs/analysis.yaml`;
change it only with a documented analysis-version increment.
