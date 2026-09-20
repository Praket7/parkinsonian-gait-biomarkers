# Common feature mapping

| Feature | WearGait source | CARE-PD source | Units | Compatibility |
| --- | --- | --- | --- | --- |
| cadence | walkway or foot contacts | ankle/foot contacts from 3D motion | steps/min | high |
| step time | walkway or foot contacts | ankle/foot contacts from 3D motion | s | high |
| stride time variability | same-foot contacts | same-foot contacts | % | moderate |
| gait speed | walkway translation | global 3D translation when valid | m/s | moderate |
| step-length asymmetry | walkway left/right step lengths | left/right foot trajectories | % | moderate |
| arm swing ROM | wrist relative to trunk | wrist relative to trunk | deg | moderate |
| trunk acceleration RMS | trunk IMU | trunk/torso kinematics | m/s2 | low |

Features are externally replicated only when the operational definition and units are comparable.
