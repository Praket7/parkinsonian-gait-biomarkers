# v4.2 reporting addendum

This addendum clarifies the immutable v4.2.0 analytical bundle; it does not alter its protocol, outputs, or v4.1 conclusions.

## H4: documented data-provenance boundary

The raw V1 and longitudinal releases were audited across 1,600 and 863 CSV files, respectively. Both contain `Time`, left/right foot-contact streams, `Walkway_X`, `Walkway_Y`, and `WalkwayFoot`, so temporal contacts are recoverable. The released `Walkway_X/Y` fields are pressure-grid strings, however, not documented calibrated metric rear-foot coordinates. Step length, stride length, and gait speed therefore cannot be validated as PKMAS-equivalent. The all-eight analytical-equivalence gate did not pass, no partial 5/8 score was generated, and H4 remains `NOT_ESTIMABLE`.

This is a data-provenance limitation, not evidence that the normative score is unreliable. It should not be revisited unless the data owners release a documented grid-to-metric calibration or PKMAS footfall coordinates.

## H2-R: reproducible rank information, not absolute-score prediction

Across 100 repeated participant-grouped five-fold validations, adding the frozen severity-blind score produced consistent rank improvement beyond gait speed:

| Evaluation unit | Median delta Spearman | Repetitions with improved Spearman | Median delta RMSE | Repetitions with improved RMSE |
| --- | ---: | ---: | ---: | ---: |
| Row-level SP/HP records | +0.0545 | 99% | +0.0123 | 25% |
| Participant-level mean held-out prediction | +0.0474 | 98% | -0.0069 | 66% |

The nested ridge sensitivity was concordant: median delta Spearman was +0.0509, median delta MAE was -0.0113, and median delta RMSE was +0.0105. Regularization does not establish a consistent absolute-error advantage.

The frozen v4.2 label is therefore `RANKING_SUPPORT_ONLY`: the score contributes reproducible incremental information about Parkinsonian gait-severity ordering beyond gait speed, while superior exact clinical-score prediction remains unestablished. This does not change v4.1's original H2 conclusion.
