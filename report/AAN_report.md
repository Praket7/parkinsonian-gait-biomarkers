# Separating trait from state in Parkinsonian gait: an authorized secondary analysis

## Bottom line

The strict, predeclared trait screen was **not supported**. Several reference-walkway measures were associated with worse MDS-UPDRS Part III gait-item score, but no measure simultaneously showed an FDR-controlled association, stable participant-bootstrap direction, validated temporal sensing where required, and adequate two-session repeatability. These data support associations and a cautious translation-only external check; they do not establish a clinical biomarker, diagnostic test, causal mechanism, or medication effect.

## Data and unit of analysis

WearGait-PD V1 was analysed from the released PKMAS pressure-walkway summary for the two available reference tasks: self-paced (SP) and hurried-paced (HP) walking. The joined table comprised 271 participant-task rows; the PD primary cohort comprised 124 usable task rows from 62 participants with MDS-UPDRS Part III item 3.10 (gait). Thirteen rows without an exact clinical-ID match or required analysis value were not used in the primary model. The authorized source data remain outside this public repository.

The primary model was a Gaussian GEE clustered by participant, with standardized outcome and gait-item score, adjusted for age, height, sex, task, and acquisition site. Benjamini-Hochberg correction covered the 11 predeclared reference measures. Direction stability used 2,000 whole-participant bootstrap resamples. This preserves task rows while avoiding individual-walk resampling.

## Primary associations

Higher gait impairment was associated with lower speed (standardized beta -0.308, 95% CI -0.464 to -0.151, q=0.00042), shorter step length (-0.367, -0.511 to -0.223, q=0.0000032), and shorter stride length (-0.375, -0.519 to -0.231, q=0.0000032). Temporal variability and support-phase measures also survived FDR: step-time CV (0.453, q=0.0135), stride-time CV (0.347, q=0.0487), stance fraction (0.277, q=0.0135), swing fraction (-0.277, q=0.0135), and double-support fraction (0.290, q=0.0135). Cadence, mean step time, and mean stride time did not survive FDR.

The variance model indicates that step/stride length and support-phase measures had large participant-level fractions (about 0.71 to 0.76), while speed and cadence also had substantial task/site fixed-context fractions (about 0.32). This is descriptive model decomposition, not evidence that a feature is a stable trait by itself.

## Signal and longitudinal checks

The raw WearGait contact stream was restricted to release-labelled `Walk` segments and split at gaps over two seconds. Against independent PKMAS measurements across 257 matched trials, contact cadence had Spearman rho=0.962 (MAE 2.54 steps/min) and mean step time rho=0.960 (MAE 0.0125 s). Only those two temporal measurements were treated as validated contact proxies.

In the longitudinal release, 184 participant-task session pairs were available for cadence, step time, and step-time CV. ICC(2,1) was 0.610 for cadence, 0.587 for mean step time, and 0.808 for step-time CV. Crucially, there is no linked repeated clinical-score table in the accessible longitudinal files, so no within-person severity-change or medication-effect model was fitted.

## CARE-PD check

CARE-PD's canonicalized SMPL translations were used only for a narrow, external translation check. After retaining plausible, forward-axis trajectories (2,893 trials; 110 cohort-qualified participants), a cohort-adjusted participant-clustered model showed lower global translation speed with higher gait label (beta -0.656, 95% CI -0.765 to -0.547, p=3.7e-32). This agrees directionally with the WearGait speed association, but is **not** a gait-event, spatial-feature, or clinical biomarker replication: CARE-PD's reconstructed motion and heterogeneous cohorts do not provide an operationally identical outcome.

## Conclusion

The data reject the stronger claim that this implementation has identified a context-robust trait biomarker. They do provide reproducible evidence that several walkway features co-vary with gait impairment, and that speed has a directionally consistent, limited external translation check. A future confirmation study needs independently scored longitudinal visits, a prespecified medication-state protocol, and an external reference-walkway replication before any measure is promoted to a trait biomarker.

All aggregate outputs and decision thresholds are recorded in `results/frozen/results.json`; participant-level files and derived row-level tables are deliberately excluded from version control.
