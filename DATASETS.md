# Dataset guide

The project uses separate datasets to answer separate questions. Their measurements are not interchangeable. The public repository contains source descriptions and permitted summary results. It does not contain participant records.

## WearGait PD

The first release has 185 people, including 100 with Parkinson’s disease plus 85 control participants. It includes wearable sensors, pressure walkway measures, video notes, clinical measures, and demographic details. This is the main source for the one visit analysis.

The longitudinal release follows 47 people with Parkinson’s disease across visits at least six months apart. The first visit overlaps the first release. Do not count that visit as a new person. The available task files do not provide a verified repeated clinical score linked to each session. The analysis therefore measures long interval score stability, not short term repeatability or clinical response.

Both releases are hosted through [Synapse](https://www.synapse.org/). File access requires an account plus acceptance of the applicable data terms. The source project states a CC BY 4.0 license. Follow the current source terms before reuse.

## CARE PD

CARE PD combines movement records from nine cohorts at eight centers. Each record uses a computer model of body movement. This can help researchers study differences between sites. It does not use the same eight pressure walkway measures as the frozen WearGait score. No validated conversion currently lets us apply that score to CARE PD.

The project record is available through [Borealis Dataverse](https://doi.org/10.5683/SP3/TWIKMK) plus [Hugging Face](https://huggingface.co/datasets/vida-adl/CARE-PD). The listed terms are CC BY NC ND 4.0. Read the current access terms before use.

## Mobilise D

The CVS release contains repeated real world mobility measures across five visits. It offers a separate test of how selected walking measures change with broad motor severity. It is not combined with WearGait. The archive is available from [Zenodo](https://doi.org/10.5281/zenodo.21060991) under CC BY NC ND 4.0.

## Mendeley gait assessment

Processed tables support separate checks against a second dataset, six month change, plus medication timing. Raw records are not joined to processed participant IDs. The source is [Mendeley Data](https://doi.org/10.17632/gdgw7m36v3.2), listed under CC BY 4.0.

## Adaptive DBS

The source may support a future state response question. A reliable mapping between recordings and clinical state pairs has not been established. No treatment effect is claimed. The source record is [Zenodo](https://zenodo.org/records/19371521).

## Local setup

Keep authorized source files outside the Git repository, such as in a controlled Drive folder. Set `PARKINSON_GAIT_DATA_ROOT` to the folder that contains these names.

```text
WearGait_PD_V1
WearGait_PD_Longitudinal
CARE_PD
MobiliseD_CVS_v1_0_0
Mendeley_Gait_PD_v2
AdaptiveDBS_Gait_2026
```

The pipeline writes participant level audit files to local result folders ignored by Git. Only permitted aggregate outputs belong in version control. Drive placeholders may need temporary source downloads. A full authorized analysis can need substantial free disk space. Missing credentials, unavailable files, or insufficient space stop acquisition. None of those conditions is evidence against a scientific hypothesis.

## Local source notes

The `data/metadata` folder contains public metadata snapshots plus acquisition manifests. Run `python scripts/acquire_dataset_metadata.py` to refresh public metadata. That script does not sign in, accept data terms, request access, or download participant files.

Dataset descriptions can change. Confirm current access rules, source versions, and license terms at the source before reuse.
