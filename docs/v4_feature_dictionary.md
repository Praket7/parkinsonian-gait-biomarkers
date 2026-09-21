# v4 feature dictionary

The canonical formulas, source requirements, minimum cycle count, and intended context of use are frozen in [`configs/v4_feature_definitions.yaml`](../configs/v4_feature_definitions.yaml). The `_v1` suffix deliberately distinguishes every prospective candidate from the frozen v3.2.4 features.

`context_adjusted_gait_deviation_v1` is control-trained only: severity is neither a training target nor a composite weight. `stride_scaling_response_v1` and `cadence_scaling_response_v1` are motor-challenge measures, not speed-independent traits.
