# v4.4 measurement-error and responsiveness extension

v4.4 is a prospective extension of v4.3, not a revision of any frozen score, feature, threshold, or conclusion. Its new endpoint is the featurewise median across exactly four valid, independently reconstructed walkway passes within each task and session. The v4.1 control-reference model is serialized and applied unchanged.

## Locked decisions

- Four valid passes are required in both sessions. A session with fewer valid passes is excluded; no pass is imputed.
- The endpoint aggregates the eight reconstructed inputs before scoring. It does not select the best pass or average observed scores after inspecting outcomes.
- The primary reliability statistic is between-session ICC(A,1) of the declared session endpoint, with 2,000 participant bootstrap resamples. The pass-level variance decomposition reports participant, session-within-participant, and residual-pass variation, plus SEM and MDC95.
- The lower bound of the 95% ICC interval must be at least 0.80 to qualify the new endpoint. Failure cannot alter the v4.3 result.

## Estimability gates

Clinical responsiveness requires repeated MDS-UPDRS Part III at each longitudinal gait session and medication state/time since medication. The authorized longitudinal task CSV schema lacks these linked fields, so no surrogate clinical endpoint is fitted. Internal-external site transport has exactly one overlapping documented label, VA Seattle. A control-only reference derived from the other site can therefore be applied to that one holdout without clinical-outcome tuning, but it is labeled `INCOMPLETE` because one site cannot establish general transport.

This protects the central conclusion: analytical validity, reliability, responsiveness, and transport are separate evidence layers. See the generated aggregate-only [v4.4 report](../results/v4_4/AAN_v4_4_report.md).

Reporting both relative reliability and absolute measurement error follows
instrumented-walkway synthesis and Parkinson-specific test-retest studies
([8](../report/AAN_bibliography.md#bibliography), [9](../report/AAN_bibliography.md#bibliography),
[10](../report/AAN_bibliography.md#bibliography)). These sources motivate the
protocol; they do not justify relaxing the project’s frozen 0.80 lower-bound rule.
