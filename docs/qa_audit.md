# Quality-control audit (2026-09-20)

Status: **software release gate passed; clinical translation remains no-go**.
The authorized analysis completed, but its strict trait criterion is empty and
the missing repeated clinical-score table prevents a progression or medication
claim.

## Completed checks

- Raw WearGait contact files are restricted to labelled `Walk` segments, with
  pauses over two seconds split before event features are calculated.
- Reference PKMAS walkway values, not inferred spatial signals, are the V1
  primary outcomes. Contact cadence and mean step time achieved rho=0.962 and
  0.960 against 257 matched walkway trials.
- The primary GEE clusters by participant, adjusts for prespecified context and
  demographics, reports CIs, controls the FDR family, and uses 2,000
  whole-participant bootstrap resamples.
- A mixed-model variance summary and longitudinal ICC/SEM/MDC table are
  generated. CARE-PD is held apart and only used for translation-speed QC.
- `python -m unittest discover -s tests -v` passed 13 tests and
  `python scripts/qa_release_gate.py` passed after the completed run.

## Remaining scientific gates before a clinical conclusion

1. Obtain or link independently scored longitudinal clinical visits before a
   within-person severity-change or medication-state claim.
2. Repeat the full reference-walkway feature set in a held-out external cohort;
   CARE-PD translation is not a substitute.
3. Add an independently held-out site/device transport analysis and negative
   controls before labelling a measure context robust.

## Source-backed boundary

WearGait-PD's source paper describes a synchronized multi-sensor dataset and
requires Synapse registration and pledge/data-use compliance before access:
<https://pmc.ncbi.nlm.nih.gov/articles/PMC13009270/>. CARE-PD is a heterogeneous
multi-site benchmark with cohort-specific labels and generalization protocols:
<https://arxiv.org/abs/2510.04312>. Digital measures require analytical and
clinical validation appropriate to their intended context of use, including
reliability and independent validation:
<https://www.nature.com/articles/s41746-020-0305-8>.

Until those gates are met, the defensible conclusion is “severity-associated
features observed, but no context-robust trait biomarker identified.”
