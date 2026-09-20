# Separating Trait from State in Parkinsonian Gait

## Status

This is a methods-complete, results-pending report. Public metadata confirm
that the planned datasets contain the modalities needed for the study, but the
participant-level records were not downloaded or analyzed because access
requires dataset-specific terms and, for WearGait, a registered Synapse
account. Therefore no hypothesis is accepted or rejected and no clinical
claim is made.

## Prespecified method

The analysis operates at participant-task/session level, uses a small
interpretable feature registry, preserves task and site labels, rejects
unknown tasks, and applies participant-cluster resampling. The primary output
is an adjusted association table with confidence intervals and FDR values; the
external dataset is never used to tune the discovery analysis. The complete
frozen design is in `docs/preregistration.md`.

## Conclusion

No trait-like, state-responsive, or context-confounded gait feature can be
classified until the authorized data are supplied and the pre-specified checks
run. That is an access boundary, not a negative clinical finding.
