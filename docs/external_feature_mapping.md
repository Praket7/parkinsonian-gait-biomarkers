# External feature mapping

| Source dataset | Source variable | Canonical feature | Unit | Compatibility | Primary external family | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| Mendeley | mean stride speed | `stride_speed_mean` | source-defined | construct-level | no | Must not be relabeled as walkway speed without definition review. |
| Mendeley | mean stride amplitude | `stride_amplitude_mean` | source-defined | source-specific | no | Not assumed equivalent to stride length. |
| Mobilise-D | source dictionary walking speed | `gait_speed` | m/s after dictionary verification | construct-level | yes | Pace-domain monitoring candidate. |
| Mobilise-D | source dictionary stride length | `stride_length_mean` | m after dictionary verification | construct-level | yes | Do not call exact replication unless operational definitions match. |
| Mobilise-D | source dictionary cadence | `cadence` | steps/min after dictionary verification | construct-level | yes | Confirmatory overlapping feature. |
| Mobilise-D | source dictionary stride duration | `stride_time_mean` | s after dictionary verification | construct-level | yes | Confirmatory overlapping feature. |
| Adaptive DBS | aligned gait outcome | source-specific | source-defined | state-response only | no | Never counts as progression evidence. |
