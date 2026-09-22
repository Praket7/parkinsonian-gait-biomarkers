# Common feature mapping

| Feature | WearGait source | CARE-PD source | Units | Compatibility |
| --- | --- | --- | --- | --- |
| cadence | walkway or validated foot contacts | not extracted in this analysis | steps/min | WearGait-only |
| step time | walkway or validated foot contacts | not extracted in this analysis | s | WearGait-only |
| stride time variability | same-foot contacts | not extracted in this analysis | % | WearGait-only |
| gait speed | walkway translation | canonical global translation only after forward-axis QC | m/s | limited directional check |
| step-length asymmetry | walkway left/right step lengths | left/right foot trajectories | % | moderate |
| arm swing ROM | wrist relative to trunk | wrist relative to trunk | deg | moderate |
| trunk acceleration RMS | trunk IMU | trunk/torso kinematics | m/s2 | low |

Features are externally replicated only when the operational definition and units are comparable. The completed CARE-PD check is explicitly not labelled a feature replication because it uses reconstructed global translation rather than matched gait events or walkway reference measures.

## Frozen eight-input score bridge (v4.5)

The authorized CARE-PD release contains canonical SMPL pose/translation records,
not PKMAS walkway footfalls or an official matched eight-feature table. The
required outcome-blind bridge has no reference measurements with which to
validate the following transformations:

| Frozen input | Required CARE-PD equivalence evidence | Status |
| --- | --- | --- |
| gait speed | Same travel segment and metric displacement/duration as PKMAS | `NOT_VALIDATED` |
| cadence | Left/right contact event agreement and identical bout boundaries | `NOT_VALIDATED` |
| mean step length | Calibrated alternating-foot spatial contacts | `NOT_VALIDATED` |
| mean stride length | Calibrated same-foot spatial contacts | `NOT_VALIDATED` |
| mean step time | Alternating-foot contact timing agreement | `NOT_VALIDATED` |
| mean stride time | Same-foot contact timing agreement | `NOT_VALIDATED` |
| step-time CV | Matched event inclusion, variability definition, and minimum steps | `NOT_VALIDATED` |
| stride-time CV | Matched event inclusion, variability definition, and minimum strides | `NOT_VALIDATED` |

Clinical UPDRS or medication labels cannot be used to pick a transform. Until
these measurements are independently validated, the frozen score, multi-center
leave-one-center-out transport, and paired score medication response are
`NOT_ESTIMABLE` in CARE-PD. Canonical translation speed remains a separate,
limited check.
