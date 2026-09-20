# Analysis deviations ledger

This ledger records what the public repository does and does not establish. It
is an audit record, not a replacement for the preregistration or the final
results. “Not estimable” means the required evidence was unavailable or not
implemented; it is not a negative finding.

| Planned item | Current classification | Scientific consequence |
| --- | --- | --- |
| Feature-specific PASS/FAIL/NOT_ESTIMABLE evidence rules | Implemented in v3.1 evidence matrix, reconstructed by release QA | An unavailable evidence path is not silently turned into a failed proxy requirement. |
| Correct ICC(A,1) with confidence interval | Implemented task-specifically with bootstrap 95% intervals, SEM, and MDC95 | The results describe task-specific repeatability; low ICC remains a real limitation. |
| Speed-adjusted and task-specific primary sensitivity models | Implemented | Several primary severity associations attenuate after speed adjustment or vary by context. |
| Leave-site-out robustness | Implemented with one canonical boolean sign function | Stored site consistency and its PASS/FAIL decision must exactly reconstruct from frozen context rows. |
| WearGait longitudinal clinical-score join | NOT_ESTIMABLE after filename/header, MAT/HDF5 schema, and Synapse metadata audits | Repeated clinical change was not fitted because no joinable participant/session/clinical-score structure was found. |
| CARE-PD cohort-level and medication-state analyses | Restricted to four UPDRS-labelled cohorts, with three translation-speed sensitivities and conditional BMCLab ON/OFF summaries | This is `LIMITED_TRANSLATION_CHECK`, not matched gait-event feature replication. |
| CARE-PD matched temporal features | NOT_ESTIMABLE after canonical-schema inspection | Canonical records expose pose/root translation but not foot/ankle trajectories or event arrays; contacts are not fabricated from pose. |
| Analysis version/config/result agreement | Enforced for v3.1 | The release gate checks version, FDR, evidence reconstruction, numeric trace, aggregate hashes, and publication privacy. |
| Negative controls | Implemented | Gaussian-feature, shuffled-severity, and site-only controls did not show a strong primary association. |
| Run provenance manifest | Schema v2 distinguishes analysis and release commits | It records that authorized external row-level data were used, while no row-level data were recorded or published. |

## Interpretation boundary

The defensible current statement is that the implemented pipeline did not
establish a context-robust trait biomarker. It does not establish that every
candidate feature truly failed, because several required evidence paths remain
not estimable. The public repository contains metadata and aggregate outputs;
authorized row-level inputs remain outside the repository.
