# When association is not validation

## Testing a control referenced Parkinsonian gait measure

This is the canonical AAN research report. The scientific results are frozen at v4.5.1. This submission organizes those results without changing the score, models, thresholds, or participant level analyses.

## Abstract

Parkinson disease alters basal ganglia circuits that help scale and automate movement, and these changes can appear in gait. Yet a gait measure can correlate with clinical severity without being stable enough for longitudinal biomarker use. Rather than treating association as validation, this study tested the same outcome-blind, healthy control referenced gait deviation score across separate evidence layers.

The score quantified multivariate deviation across eight gait features from an age and height adjusted healthy control reference without using Parkinson severity outcomes. The primary analysis included 62 participants with Parkinson disease. The score was associated with gait specific MDS UPDRS severity, with a standardized effect of 0.301, 95% CI 0.089 to 0.513, and q = 0.0055. After adjusting for walking speed, the effect remained 0.279, 95% CI 0.083 to 0.475, with q = 0.0053. The association retained the same direction in all 2,000 healthy control reference resamples. Participant level Spearman ranking improved in 98 of 100 participant grouped validation repetitions, with median change of 0.047. All eight reconstructed inputs also passed prespecified analytical agreement criteria across 252 matched raw walkway trials.

Despite these positive results, the same fixed score failed the prespecified six plus month stability criterion. Self paced ICC was 0.647 and hurried pace ICC was 0.282. Because visits were at least six months apart, this reflects long interval stability rather than controlled short term repeatability and may include true clinical or medication related change.

These findings show that clinical association, analytical agreement, and better severity ranking do not by themselves establish longitudinal biomarker stability. A digital gait measure can pass several conventional checks and still fail an important longitudinal criterion.

## Clinical problem and research gap

Parkinson disease changes the brain systems that help initiate, scale, and automate movement. Those changes can affect stride length, speed, timing, and gait variability. Digital gait measures can therefore provide objective descriptions of motor behavior, but a useful association with severity is only one part of biomarker validation.

A measure can correlate with a clinical rating and still depend heavily on walking speed, the healthy reference sample, the measurement system, or the time between visits. It can also rank participants better without improving exact clinical score prediction. This project separates those questions instead of treating one positive statistic as proof that a biomarker is ready for longitudinal use.

## Research question

The study asked whether a fixed gait deviation score defined relative to healthy walking captured gait specific Parkinsonian severity beyond walking speed, and whether the same score remained defensible when tested for reference robustness, incremental ranking, analytical measurement agreement, and long interval stability.

The score was intentionally outcome-blind. Parkinson severity outcomes were not used to fit the healthy reference or define the eight input features.

## Study design

The primary WearGait analysis included 62 independent participants with Parkinson disease. Repeated task observations were clustered by participant, and participant grouped validation kept records from the same person in the same fold.

The score used eight frozen gait inputs.

1. Gait speed
2. Cadence
3. Mean step length
4. Mean stride length
5. Mean step time
6. Mean stride time
7. Step time coefficient of variation
8. Stride time coefficient of variation

The healthy reference estimated the expected multivariate gait pattern for age and height. The score quantified how far a measured gait pattern departed from that reference while accounting for correlations among the eight inputs.

## Primary severity association

The score was associated with concurrent gait specific MDS UPDRS severity. The standardized effect was 0.301 with a 95% confidence interval from 0.089 to 0.513 and q = 0.0055.

Walking speed is a strong summary of mobility, so the study also tested whether the score contained information beyond speed. After adjustment for walking speed, the standardized effect remained 0.279 with a 95% confidence interval from 0.083 to 0.475 and q = 0.0053.

This supports a severity association beyond simple walking speed. It does not mean the score replaces the clinical rating.

## Healthy reference robustness

The healthy control reference was resampled 2,000 times while the score definition stayed fixed. The severity association retained the same direction in all 2,000 resamples, and the median standardized effect was 0.291.

This test asks whether the result depends strongly on the particular people who happened to form the healthy reference sample. The directional consistency supports robustness to that source of variation, but it is not independent clinical replication.

## Incremental information beyond speed

The score was compared with a speed only baseline across 100 repeated participant grouped validations. Participant level Spearman ranking improved in 98% of repetitions, with a median change of about +0.047.

The exact score prediction results were weaker. RMSE improved in 66% of repetitions, MAE improved in 44%, Pearson correlation improved in 91%, calibration slope was closer to its ideal value in 60%, and calibration intercept was closer to its ideal value in 61%.

These results support improved severity ordering more strongly than improved absolute prediction. Ranking and numerical prediction error are different questions and are kept separate in the interpretation.

## Analytical measurement agreement

Before using the score for repeated visits, the study checked whether the same eight inputs could be reconstructed from raw walkway records. The reconstruction was compared with PKMAS values on 252 matched trials.

All eight inputs passed the prespecified analytical agreement gates. Mean features were required to meet stricter agreement thresholds than variability features, and the gates were fixed before the final interpretation.

This result supports the WearGait measurement bridge. It does not by itself establish clinical validity, treatment response, or equivalence in a different device or dataset.

## Long interval stability

The same fixed score was then applied to repeated visits separated by at least six months. The prespecified stability criterion was not met.

Self paced walking had ICC = 0.647 with 45 paired participants. Hurried walking had ICC = 0.282 with 44 paired participants. Both failed the frozen criterion.

This is an important negative result. The visits were separated by at least six months, so the comparison includes possible disease progression, medication related state changes, health changes, and measurement variation. It therefore measures long interval stability under changing clinical conditions. It does not estimate controlled short term test retest reliability.

## What the project contributes

The main contribution is the validation architecture applied to one fixed score. The study does not claim that gait features, multivariate distance scores, or Parkinson digital biomarkers were invented here.

Instead, the project shows why several evidence layers must be separated.

| Evidence layer | Result | Interpretation |
| --- | --- | --- |
| Concurrent severity association | Supported | The score was associated with gait specific severity |
| Speed adjusted association | Supported | The association remained after accounting for walking speed |
| Healthy reference robustness | Supported | Direction was retained across all 2,000 reference resamples |
| Severity ranking beyond speed | Supported | Ranking improved in 98% of participant grouped validations |
| Exact score prediction | Incomplete | Error and calibration metrics did not improve consistently |
| Analytical reconstruction | Supported | All eight inputs passed agreement gates across 252 trials |
| Six plus month stability | Failed | The fixed score did not meet the prespecified criterion |
| Short term repeatability | Not estimable | The available repeated visits were too far apart |
| Clinical responsiveness | Not estimable | Verified session linked clinical anchors were unavailable |
| Broad external transport | Not established | Measurement equivalence across sites and systems remains incomplete |

The key scientific lesson is that positive association, strong analytical agreement, and better ranking can coexist with failed longitudinal stability. Those findings are not contradictory. They answer different questions.

## Claim boundaries

This study is not a diagnosis of Parkinson disease. It does not establish a diagnostic threshold, a treatment response biomarker, patient benefit, short term test retest reliability, or broad multisite calibration.

The supported claim is narrower. The fixed control referenced score contains severity ranking information beyond gait speed in the primary dataset and can be reconstructed from audited WearGait walkway records, but it did not meet the prespecified six plus month stability standard.

## Limitations

The primary sample contains 62 independent participants, which is modest for clinical biomarker work. The clinical anchor is gait specific rather than a complete measure of Parkinson disease burden. The long interval visits cannot isolate measurement noise from true clinical change. Secondary datasets use different representations and do not provide a complete validated bridge to every frozen input. A one site sensitivity analysis cannot establish broad transport.

The project also does not test a causal neural mechanism. Basal ganglia dysfunction provides the neurological rationale for examining gait, but the score itself is a behavioral motor measure.

## Next experiments

The highest value next experiment is a short interval repeated walk study that keeps task, device, and medication timing as controlled as possible while recording matched MDS UPDRS gait ratings at every session.

A second priority is independent site validation. The eight input measurement bridge should be established before the fixed score is tested at the new site, and the target site should not be used to retune the score.

A prospective study should then confirm participant level ranking, absolute error, calibration, and longitudinal behavior as separate outcomes.

## Conclusion

The score shows a clear cross sectional severity signal beyond walking speed, strong reference robustness, improved participant severity ranking, and analytical agreement across the eight frozen gait inputs. Yet the same fixed score failed the six plus month stability criterion.

That negative result strengthens the scientific interpretation because it prevents association from being mistaken for longitudinal qualification. Digital gait biomarkers should be judged by the specific use they are meant to serve, and each evidence layer should be tested on its own.
