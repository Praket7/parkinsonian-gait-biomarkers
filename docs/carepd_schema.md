# CARE-PD schema audit

The downloaded archive contains nine top-level cohort pickles: `3DGait`,
`BMCLab`, `DNE`, `E-LC`, `KUL-DT-T`, `PD-GaM`, `T-LTC`, `T-SDU`, and
`T-SDU-PD`. Each is a nested mapping of `participant -> trial -> record`.

Every inspected trial record has:

- `pose`: `(frames, 72)` `float32` SMPL pose values
- `trans`: `(frames, 3)` `float32` translations
- `beta`: `(1, 10)` shape parameters
- `fps`: positive recording rate, observed at 25, 30, and 150 Hz
- `UPDRS_GAIT`: integer gait item score
- `medication`: often `None`; BMCLab includes `on`/`off`
- `other`: cohort-specific metadata, including `freezers` in BMCLab

The source does not provide the wearable event arrays used by the primary
pipeline (`left_contacts`, `right_contacts`, step lengths, and so on). CARE-PD
therefore supports replication from SMPL sequences or derived kinematics, not
direct pooling of the existing wearable feature table. The reader in
`src/carepd.py` extracts trial metadata and validates shapes while preserving
raw arrays. Fold pickles are split definitions, not additional observations,
and are excluded by default.

Valid now: trial-level counts, frame-rate/length summaries, UPDRS-GAIT
associations after a separately specified SMPL-derived feature extractor, and
cohort-held-out analyses. Not valid without additional derivation: claiming
equivalence to WearGait features, medication-response effects where medication
is missing, or participant-level longitudinal change from the single-visit
cohorts.
