# Research review: context-robust Parkinsonian gait biomarkers

## Bottom line

Treat the proposed output as a **context-aware digital gait measure** (or a candidate monitoring/progression marker), not a diagnostic biomarker, unless the study is explicitly designed and powered for diagnosis against an expert clinical reference standard. Parkinson disease diagnosis still depends on trained neurologic history/examination under the MDS criteria; a gait signal alone cannot establish PD. The MDS notes that supportive features increase confidence but cannot make the diagnosis on their own ([MDS position statement](https://www.movementdisorders.org/MDS/News/Newsroom/Position-Papers/MDS-Position-Diagnosis-of-PD.htm)).

The defensible scientific question is: **Does a pre-specified gait measure retain analytical reliability and clinically meaningful association with a prespecified outcome across walking contexts, medication states, sites, devices, and people?** Avoid the stronger claim that one model is “context robust” simply because it scores well on randomly split windows.

## What is reasonably supported

- Candidate outcomes with the strongest current support include stride length, stride-time variability (SD or coefficient of variation), turn velocity/turn steps, trunk range of motion, arm-swing range, and foot-contact/shuffling measures. The NINDS PD digital-outcomes guidance lists these as recommended gait outcomes, while noting that most evidence remains from prescribed tasks ([NINDS PD digital outcomes guidance](https://www.commondataelements.ninds.nih.gov/sites/nindscde/files/Doc/PD/F3012_Best_Practices_for_Digital_Health_Outcomes.pdf)).
- Free-living signals can be treatment-responsive without being disease-specific. In Parkinson@Home, real-life gait features detected medication-related motor fluctuations (combined AUC 0.84), whereas distinguishing PD from controls was weaker (AUC 0.76); hand position materially changed wrist/pocket spectral features ([Hillel et al., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC7584982/)). This is direct evidence that context and sensor placement are part of the measurement, not nuisance details to ignore.
- Freezing of gait is especially context-dependent: narrow spaces, turning, obstacles, transitions, and medication state can elicit episodes that a broad hallway test misses. A wearable FOG study used synchronized video/manual annotation and leave-one-patient-out validation; its reported sensitivity/specificity are useful feasibility results, not proof of generalization to arbitrary homes or populations ([Mazilu et al./FOG-provoking test](https://pmc.ncbi.nlm.nih.gov/articles/PMC7472497/); [daily-living FOG comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC10071496/)).
- Technical validity and clinical validity are separate. A wearable gait system can agree with motion capture on stride parameters in a standardized walk yet still fail to represent daily-life mobility. Conversely, a daily-life signal can correlate with clinical state without being accurate as a stride-event measurement. Both layers need to be reported ([sensor-vs-motion-capture validation](https://pmc.ncbi.nlm.nih.gov/articles/PMC8623101/)).

## Main infeasible or unsafe claims to remove

1. **“Diagnoses Parkinson’s from gait.”** Replace with “estimates a prespecified gait phenotype,” “monitors motor fluctuations,” or “tests association with clinically rated parkinsonism.” A control-vs-PD classifier is not a diagnostic device without representative differential-diagnosis cohorts, expert reference diagnosis, prospective external validation, calibration, and a clinical-use threshold.
2. **“Works regardless of context.”** Context changes the estimand. Define the intended context of use (e.g., 10-m walk, turning task, home free-living walking, or a specific walking-bout class), then test transport across contexts. If context labels are available, report stratified performance and interaction terms rather than averaging them away.
3. **“Progression biomarker” from cross-sectional severity correlation.** Cross-sectional association supports a correlate, not progression. Progression requires longitudinal repeated measures, prespecified follow-up, reliability/MDC, sensitivity to change, and a clinically interpretable anchor.
4. **“Freezing detector” from unannotated activity data.** FOG episodes require an operational definition and synchronized reference annotation (video, clinician rating, or another justified reference). Report event-level sensitivity, false alarms per hour/walking bout, onset latency, and missingness—not only window accuracy.
5. **“Generalizes” from random window splits.** Windows from the same person leak subject-specific gait, device placement, and environment. The minimum split is subject-wise; stronger evidence is leave-one-site/device/context-out plus a locked external test set.

## Recommended implementation and validation plan

### 1. Lock the estimand before modeling

Choose one primary use and one primary outcome. For example: “weekly median stride-time CV during free-living walking as a monitoring measure of motor fluctuation,” or “event-level FOG detection during turning and narrow-space tasks.” Keep diagnosis, progression, and treatment response as separate claims; FDA/NIH biomarker categories require different validation evidence.

Record, at minimum: medication state and time since last levodopa dose, sensor location/orientation/firmware, walking-bout segmentation rules, assistive device, footwear, terrain/surface, indoor/outdoor status, turns/obstacles, time of day, and missingness. NINDS specifically recommends sharing participant, PD, technology, and environment/context metadata and warns that medication and narrow-space walking can alter outcomes ([NINDS PD v2 digital subgroup summary](https://commondataelements.ninds.nih.gov/sites/nindscde/files/Doc/PD/F3018_Digital_Technology_Subgroup_Summary.pdf)).

### 2. Start with interpretable features and a context-aware baseline

Use a small prespecified feature set: stride time/length, cadence, stride-time CV, double-support time, turn velocity/steps, bout duration, and FOG burden if annotated. Establish a mixed-effects or regularized baseline with participant-level random intercepts and context/medication covariates before any deep model. Report both raw and context-adjusted estimates; adjustment is not permission to erase clinically meaningful context effects.

### 3. Evaluate robustness as transport, not as one score

Use nested subject-level splits for development, then a locked external test. Add stress tests: unseen participant, site, device, sensor placement, medication state, indoor/outdoor, straight walking versus turning, and short versus long bouts. Report confidence intervals, calibration, subgroup performance, and missing-data behavior. For continuous measures use ICC/CCC, Bland–Altman limits, MAE, and MDC; for event detection use sensitivity, specificity/precision, F1 only alongside false alarms per hour and event timing error.

### 4. Validate the measurement chain

Analytical validation: repeatability, sensor-placement sensitivity, timestamp/dropout handling, gait-event accuracy against motion capture/pressure walkway, and prespecified quality-control failures. Clinical validation: association with MDS-UPDRS gait/FOG items, patient-reported FOG, medication ON/OFF or another relevant anchor. Clinical utility: demonstrate that the measure changes a decision or trial endpoint; correlation alone is insufficient.

### 5. Make the hypothesis falsifiable

Good primary hypothesis: “After accounting for participant and medication state, stride-time variability differs by walking context, and a context-stratified model has lower absolute error than a context-agnostic model on an unseen-site test set.”

Bad hypothesis: “Our AI detects Parkinson’s gait in all real-world situations.”

Pre-register the primary feature, outcome window, exclusion rules, split strategy, and success threshold. Treat context robustness as a testable interaction/transport property, not a marketing adjective.

## Evidence boundary

The strongest immediately defensible deliverable is a reproducible, context-labeled **candidate digital outcome** with analytical and clinical validity evidence. A clinical diagnostic claim, a disease-progression claim, or a claim of universal real-world robustness requires a substantially larger prospective, multi-site study and a locked external test set.
