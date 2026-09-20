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
