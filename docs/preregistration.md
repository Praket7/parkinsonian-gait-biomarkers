# Analysis freeze v1

This repository implements the pre-specified, interpretable feature layer for
secondary analysis of de-identified movement datasets. The primary unit is a
participant-task (with repeated sessions retained as metadata), and the
primary tasks are SP, HP, SPm, and HPm. Straight walking is preferred; turns,
TUG, door passage, and free walking are context analyses.

No participant-level split may place the same participant in both train and
test. External data are never used to tune thresholds. Features are reported
with effect sizes and uncertainty, and multiple testing is corrected before
calling a trait marker. A statistical association is not interpreted as
causal or as a clinical diagnosis.

The frozen configuration is `configs/analysis.yaml`; change it only with a
documented analysis-version increment.
