# v3.2.1 external longitudinal analysis freeze

This document is frozen before any authorized external inferential model is
run. WearGait v3.1.1 primary estimates, thresholds, feature definitions, and
trait rule are retained unchanged.

External datasets are independent evidence streams: Mendeley tests
cross-sectional direction, six-month within-person change, and medication-
timing sensitivity; Mobilise-D tests real-world longitudinal construct-level
validation; adaptive DBS tests within-person state response. PPMI is disabled
until legitimate access and an audited same-visit gait/clinical join exist.

The Mobilise-D confirmatory family is walking speed, stride length, cadence,
and stride duration only. Other DMOs are exploratory and receive a separate
FDR family. Its anchor hierarchy is exact MDS-UPDRS 3.10, then an explicitly
released gait/posture composite, then Part III total; a fallback is never
silent. Confirmatory visits must pass the source-defined reliable-week rule.

The primary Mobilise-D estimand is the participant-clustered within-person
anchor coefficient after separating each participant's mean anchor value from
their deviation from it. Longitudinal claims require effect uncertainty,
participant/visit denominators, site robustness, and SEM/MDC95 context when
estimable. Small repeated Mendeley samples use paired summaries and
participant-level inference rather than an overfit mixed model.

No result may redefine a threshold, mapping, eligibility criterion, or FDR
family. A hash mismatch is `POST_FREEZE_DEVIATION`, not confirmatory evidence.
