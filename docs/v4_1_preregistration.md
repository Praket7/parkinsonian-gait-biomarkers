# v4.1 validation-only preregistration

v4.1.0 validates the v4.0.6 `context_adjusted_gait_deviation_v1` without changing its eight inputs, source cohorts, outcome definition, or frozen v4.0.6 outputs. The control reference is fit without Parkinson clinical outcomes. The primary robustness criterion is at least 80% same-direction control-reference bootstrap effects; this is not a significance-counting exercise.

The prespecified alternatives are five-fold participant-grouped control cross-fitting and Ledoit-Wolf residual covariance sensitivity. Incremental prediction uses five-fold participant-grouped held-out ordinary least-squares models. Exactly eight leave-one-input-out analyses are descriptive. WearGait longitudinal scoring is performed only if every original input has exact or defensibly transformed equivalence. Mobilise-D analyses are limited to the four frozen pace/rhythm measures in a within/between participant model and 200 participant-half resamples.

The validation is fit-for-context: short or slow real-world bouts can degrade digital gait measurement performance, so unavailable or non-equivalent inputs remain `NOT_ESTIMABLE`, not failed or imputed. This is consistent with the Mobilise-D validation recommendations ([Hobert et al., 2023](https://doi.org/10.1186/s12984-023-01198-5)).
