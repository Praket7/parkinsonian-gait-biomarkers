# Analysis deviations ledger

This ledger records what the public repository does and does not establish. It
is an audit record, not a replacement for the preregistration or the final
results. “Not estimable” means the required evidence was unavailable or not
implemented; it is not a negative finding.

| Planned item | Current classification | Scientific consequence |
| --- | --- | --- |
| Feature-specific PASS/FAIL/NOT_ESTIMABLE evidence rules | Implemented in v3 evidence matrix | An unavailable evidence path is not silently turned into a failed proxy requirement. |
| Correct ICC(A,1) with confidence interval | Implemented task-specifically with bootstrap 95% intervals, SEM, and MDC95 | The results describe task-specific repeatability; low ICC remains a real limitation. |
| Speed-adjusted and task-specific primary sensitivity models | Implemented | Several primary severity associations attenuate after speed adjustment or vary by context. |
| Leave-site-out robustness | Implemented | The matrix records sign stability; some features fail the strict site criterion. |
| WearGait longitudinal clinical-score join | NOT_ESTIMABLE after a 1,077-file authorized-data audit | Repeated clinical change was not fitted because no joinable session-level clinical table was found. |
| CARE-PD cohort-level and medication-state analyses | Implemented as cohort-specific translation-speed and conditional BMCLab ON/OFF summaries | This is transport/translation evidence, not matched gait-event feature replication. |
| Analysis version/config/result agreement | PASS: config and frozen manifest both report 3.0 | The release gate checks this consistency. |
| Negative controls | Implemented | Gaussian-feature, shuffled-severity, and site-only controls did not show a strong primary association. |
| Run provenance manifest | Implemented for release commit `c52cfa61bbb454acb143d635277be2738c3ea6ad` | It hashes configuration, dependency lock, metadata, and public aggregate outputs without reading raw inputs. |

## Interpretation boundary

The defensible current statement is that the implemented pipeline did not
establish a context-robust trait biomarker. It does not establish that every
candidate feature truly failed, because several required evidence paths remain
not estimable. The public repository contains metadata and aggregate outputs;
authorized row-level inputs remain outside the repository.
