# v4.3 H4 raw-walkway closure

v4.3 supersedes only the v4.2 data-provenance boundary. It does not refit or otherwise alter the frozen v4.1 control-reference model.

## Coordinate contract

The WearGait-PD Supplementary Table S5 defines `Walkway_X` and `Walkway_Y` as paired coordinates of active walkway sensors and specifies 1.27 cm by 1.27 cm sensor cells. Figure S5 identifies X as the walkway's longitudinal axis. The v4.3 extractor therefore takes the centroid of the active cells assigned to the contacting foot at each documented initial-contact frame and converts X using exactly 1.27 cm per cell. It uses only `GeneralEvent == Walk` passages, left/right contact markers, and `WalkwayFoot`; it neither estimates a transform nor learns from PKMAS output.

## Locked analytical-equivalence gate

The extractor was evaluated on 252 matched V1 PKMAS trials. All eight frozen inputs passed their prespecified gate: ICC(A,1) and CCC were at least 0.90 for means and at least 0.85 for CVs, while bias was within the declared limits. This validates the raw-to-feature bridge before any longitudinal score was generated. Five raw trials were excluded because they lacked sufficient alternating contacts; no exception was imputed.

## H4 result

The serialized v4.1 model was applied without refitting to 182 reconstructed longitudinal trials. H4 is now estimable, but the repeated-session score is not qualified as stable under the 0.80 lower-confidence-bound criterion:

| Task | Paired participants | ICC(A,1) | 95% bootstrap CI | Status |
| --- | ---: | ---: | ---: | --- |
| Self-paced | 45 | 0.707 | 0.462 to 0.844 | FAIL |
| Hurried pace | 45 | 0.390 | 0.073 to 0.657 | FAIL |

This is a negative reliability result, not a reconstruction failure. The correct release labels are `estimability_status=OK` and `test_retest_status=FAIL`; the score must not be described as a qualified stable trait biomarker on this evidence.

