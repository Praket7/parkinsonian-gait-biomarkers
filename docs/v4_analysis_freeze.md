# v4 analysis freeze

The v4 freeze hashes the analysis configuration, feature definitions, preregistration, external mappings, and all `src/v4` implementation modules before the primary clinical association script may run. The manifest is stored in `results/v4/frozen/protocol_manifest.json` and is checked before outcome analysis and in tests. Protocol v4.0.2 supersedes unrun earlier freezes after outcome-blind compatibility correction and prespecified source-task narrowing to SP, HP, TUG, and free walking; unrelated balance/ancillary recordings are not a candidate-search pool.

The protocol was intentionally designed before inspecting v4 clinical associations. Unsupported raw MATLAB timetable objects are not coerced into inferred wrist or trunk signals; those families remain explicitly not estimable until an official readable export is available.
