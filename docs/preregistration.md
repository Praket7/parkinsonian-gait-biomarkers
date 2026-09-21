# Analysis freeze v3

This repository implements the pre-specified, interpretable feature layer for
secondary analysis of de-identified movement datasets. The primary unit is a
participant-task (with repeated sessions retained as metadata), and the
primary tasks are SP and HP. SPm and HPm are contact-signal reliability tasks.
Straight walking is defined by the release's `Walk` annotations, split at gaps
over 2 s, and retained only when its clean duration, contact count, missingness,
and alternation satisfy `configs/analysis.yaml`.

No participant-level split may place the same participant in both train and
test. External data are never used to tune thresholds. Features are reported
with effect sizes and uncertainty, and multiple testing is corrected before
calling a trait marker. A statistical association is not interpreted as
causal or as a clinical diagnosis.

The primary model is participant-clustered GEE adjusted for age, height, sex,
task, and site. The v3 evidence matrix records PASS, FAIL, and NOT_ESTIMABLE
separately. It requires FDR q<=0.05, whole-participant GEE bootstrap direction
consistency >=0.80, speed sensitivity where applicable, task/site robustness,
and task-specific ICC(A,1)>=0.60 when a contact feature has repeated sessions.
CARE-PD is cohort-specific translation-only evidence after forward-axis and
0.2-3.0 m/s plausibility QC. The frozen configuration is
`configs/analysis.yaml`; change it only with a documented analysis-version increment.

## v3.2.1 external longitudinal extension

The original WearGait trait rule remains unchanged. External data are never
pooled with WearGait and cannot retune its thresholds. The extension records
monitoring/progression, state-response, analytical-validity,
measurement-stability, and context-transport evidence separately. Mendeley
uses participant-visit bilateral collapse; Mobilise-D uses a source-defined
reliable-week gate and an explicit clinical-anchor hierarchy; adaptive DBS
uses within-participant state contrasts only. A hash mismatch after the
v3.2.1 freeze is `POST_FREEZE_DEVIATION`, not confirmatory evidence.
