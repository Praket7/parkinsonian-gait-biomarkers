# Scientific context and literature position

## Scope

This repository studies a candidate digital gait measure for Parkinsonian motor severity. The central question is not whether gait contains information about Parkinson disease; that is well established. The question is whether a fixed gait measure remains defensible when association, measurement agreement, reliability, responsiveness, and transport are evaluated as separate properties.

The project should therefore be interpreted as a biomarker-validation study, not as a diagnostic model and not as evidence of clinical utility.

## Neurological rationale

Parkinson disease alters basal-ganglia motor circuits involved in movement initiation, scaling, and automaticity. These changes can appear behaviorally as bradykinesia, reduced stride length, altered pace, impaired adaptation, and increased temporal variability. Instrumented gait measurement provides a quantitative view of that motor phenotype, but a behavioral signal is not a direct measurement of dopaminergic loss or a specific neural circuit.

The clinical anchor used here is gait-specific Parkinsonian severity. The project asks whether a multivariate deviation from healthy gait provides information beyond simple walking speed and whether that information survives additional validation tests.

## Why validation must be layered

Digital measures can fail in different ways:

- a feature can correlate with severity but be highly dependent on walking speed,
- a score can rank participants well but predict exact clinical values poorly,
- a derived measure can be clinically associated while being technically difficult to reproduce,
- a measure can agree with a reference system yet fail to remain stable over time,
- a result can hold in one site or device but fail to transport to another, and
- longitudinal variation can reflect real clinical change rather than measurement error.

These are different scientific questions and should not be collapsed into one accuracy number.

## Current literature

### Longitudinal Parkinson digital outcomes

Rábano-Suárez et al. reviewed digital outcomes proposed as markers of early Parkinson disease progression. Among 1,507 screened records, only 15 longitudinal studies met their criteria. The review found promising signals but concluded that the ability of digital outcomes to track disease progression remains insufficiently established and called for more standardized methodology and data sharing.

Reference: Rábano-Suárez P, Del Campo N, Benatru I, et al. *Digital Outcomes as Biomarkers of Disease Progression in Early Parkinson's Disease: A Systematic Review.* Movement Disorders. 2025;40(2):184-203. [PubMed](https://pubmed.ncbi.nlm.nih.gov/39613480/)

### External validation and reporting

Qi et al. reviewed the Parkinson digital-biomarker literature and a subset of deep-learning studies for freezing of gait. The review identified strong model performance in many studies but emphasized limited external validation and inconsistent performance reporting. That limitation is directly relevant to this repository: internal predictive performance is not treated as equivalent to independent transport.

Reference: Qi W, Shen S, Dong C, et al. *Digital Biomarkers for Parkinson Disease: Bibliometric Analysis and a Scoping Review of Deep Learning for Freezing of Gait.* Journal of Medical Internet Research. 2025;27:e71560. [PubMed](https://pubmed.ncbi.nlm.nih.gov/40392578/)

### Gait as a neurological systems-level measure

A 2026 review by Ortega-Robles et al. describes gait as an integrated output of cortical, subcortical, cerebellar, spinal, and peripheral systems. It highlights the promise of digital mobility outcomes while identifying methodological heterogeneity, limited disease-specific validation, and insufficient longitudinal evidence as major barriers to translation.

Reference: Ortega-Robles E, Treviño M, Manjarrez E, Arias-Carrión O. *Walking as a Window to the Brain: Redefining Gait in Neurology.* Medical Sciences. 2026;14(3):338. [PubMed](https://pubmed.ncbi.nlm.nih.gov/42506308/)

### Wearable and remote gait measurement

Systematic reviews of wearable gait monitoring in Parkinson disease have also found substantial variation in sensor placement, algorithms, protocols, and clinical use cases. Technical validity in a laboratory does not automatically establish ecological validity, longitudinal sensitivity, or clinical usefulness.

Reference: Salaorni F, Bonardi G, Schena F, Tinazzi M, Gandolfi M. *Wearable devices for gait and posture monitoring via telemedicine in people with movement disorders and multiple sclerosis: a systematic review.* Expert Review of Medical Devices. 2024;21(1-2):121-140. [PubMed](https://pubmed.ncbi.nlm.nih.gov/38124300/)

## Position of this project

The project does not claim to introduce gait analysis, the first Parkinson digital biomarker, or the first multivariate gait score. Its contribution is narrower and methodological.

A fixed, outcome-blind, healthy-control-referenced score is evaluated through a sequence of prespecified evidence layers:

1. concurrent association with gait-specific severity,
2. robustness to resampling of the healthy reference,
3. incremental information beyond gait speed,
4. analytical agreement of reconstructed gait inputs,
5. six-plus-month longitudinal stability,
6. clinical responsiveness where session-linked anchors are available, and
7. transport to other sites or measurement systems where an equivalent measurement bridge exists.

The current evidence supports association, healthy-reference robustness, participant-level severity ranking beyond speed, and analytical reconstruction of the eight WearGait inputs. It does not establish consistently better exact-score prediction. The six-plus-month stability criterion was not met. Short-term repeatability, treatment responsiveness, and broad multisite transport remain unresolved.

## Claim boundaries

The following claims are not supported by the current evidence:

### Diagnosis

The study does not test a diagnostic threshold, differential-diagnosis population, or prospective clinical workflow. The score should not be described as diagnosing Parkinson disease.

### Disease progression

A cross-sectional association with severity does not establish progression sensitivity. The available repeated visits are separated by at least six months and lack a verified repeated clinical anchor adequate for a formal responsiveness analysis.

### Short-term reliability

Long-interval stability is not a substitute for state-controlled test-retest reliability. Medication state, disease progression, general health, and other factors may change between visits.

### Treatment response

Medication timing or treatment labels alone are insufficient. A response analysis requires comparable repeated measurements and clinically interpretable session-linked anchors.

### Broad external validation

CARE-PD and other external datasets use different measurement representations. A full replication of the frozen eight-input score requires a validated bridge to the same inputs and an appropriate healthy reference. Cohort-specific speed associations or related gait measures should not be relabeled as replication of the frozen score.

## Why a more complex model is not the immediate priority

The primary severity dataset contains 62 independent participants. A higher-capacity model would increase flexibility and overfitting risk without resolving the principal scientific uncertainties. The current bottlenecks are measurement reliability, responsiveness, and external transport, not model complexity.

A simple model that survives independent validation layers would be more informative than a more complex model evaluated only by internal predictive performance.

## Highest-value next studies

### 1. Short-interval repeatability

Repeat the same task on the same device over a short interval while documenting medication timing, clinical state, health changes, and protocol deviations. Evaluate ICC, agreement, and measurement error using the unchanged score.

### 2. Responsiveness

Collect a gait-specific clinical rating at every gait session. Test whether within-person change in the frozen score tracks within-person change in the clinical anchor.

### 3. Independent-site measurement bridge

Validate reconstruction of all frozen inputs at another center before evaluating the score itself. Do not learn the bridge from target-site clinical outcomes.

### 4. Prospective transport

Use leave-center-out or locked external evaluation with no target-site outcome refitting. Report rank correlation, absolute error, calibration, missingness, and confidence intervals separately.

## Bottom line

The most defensible conclusion is not that a Parkinson gait biomarker has been qualified. It is that a promising control-referenced gait signal can survive several validation layers and still fail another important one. The current results show why association, analytical validity, prediction, longitudinal behavior, and external transport must be evaluated separately before a digital gait measure is treated as clinically reliable.
