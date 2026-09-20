# Pre-specified feature dictionary

| Feature | Unit | Source | Interpretation boundary |
| --- | --- | --- | --- |
| cadence | steps/min | contacts | Rhythm; depends on task and speed |
| step/stride time mean and CV | s / % | contacts | Rhythm/variability; validate events against walkway |
| stance and swing fraction | fraction | contacts | Requires trusted toe-off/contact definitions |
| gait speed | m/s | walkway | Primary speed confounder; never adjust it when it is the outcome |
| step length mean/CV/asymmetry | m / % | walkway | Normalize/adjust for height where appropriate |
| arm swing ROM/asymmetry | degree / % | wrist + trunk | Context and sensor-placement sensitive |
| trunk acceleration RMS | m/s2 | trunk IMU | Analytical validity required before clinical interpretation |

The exact registry is `src/features.py`. A feature is a candidate trait marker
only after the frozen evidence chain in `docs/preregistration.md`; a small p
value alone is insufficient.
