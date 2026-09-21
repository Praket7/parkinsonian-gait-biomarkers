# Parkinsonian gait datasets

Checked 2026-09-20. The authorized source releases were acquired to the user's controlled Google Drive folder; participant-level data and row-level derivatives remain excluded from this repository.

| Dataset | Scientific fit | Access/licence | Current status |
|---|---|---|---|
| WearGait-PD (cross-sectional) | 185 participants (100 PD, 85 controls), synchronized IMUs, sensorized insoles, gait reference, video annotations, demographics and clinical evaluations; strong fit for task/speed/site-free trait analysis. | Synapse `syn52540892`; CC BY 4.0. Data-file download requires a registered Synapse account and agreement to Synapse governance policies. | Authorized V1 archive acquired. Manifest audit found 1,865 release files present. |
| WearGait-PD Longitudinal | 47 PD participants with repeated sessions at least six months apart; supports reliability and within-person change. The first session overlaps Version 1, so do not concatenate blindly. | Synapse folder `syn74686228`; same project access route and CC BY 4.0. | Authorized archive acquired. Used for contact-feature repeatability only; no linked repeated clinical-score table was treated as available. |
| CARE-PD | 9 cohorts from 8 sites and about 363 participants, harmonized anonymized SMPL gait meshes; useful independent multi-site replication. | Borealis Dataverse DOI `10.5683/SP3/TWIKMK` and Hugging Face `vida-adl/CARE-PD`. Dataverse/HF metadata reports CC BY-NC-ND 4.0. The official HF card says users must read the project terms before downloading/using data. | Official Hugging Face revision `d53fe929aaacbd6822bcad5ef2b1d215401800b7` acquired after terms acceptance; 37 source files are checksum-recorded in `data/metadata/carepd_acquisition_manifest.json`. |
| Mobilise-D CVS V1.0.0 | Five-visit, real-world DMO cohort; separate broad-motor monitoring context. | Zenodo DOI `10.5281/zenodo.21060991`; CC BY-NC-ND 4.0. | Archive-native PD table with ≥3 valid-day gate; never pooled with WearGait. |
| Mendeley Gait Assessment | Processed Tables 1–3 provide transport, six-month, and timing contexts. | DOI `10.17632/gdgw7m36v3.2`; CC BY 4.0. | Direct workbook loading; raw and processed IDs are never joined. |
| Adaptive DBS | Potential state-response evidence only. | Zenodo record `19371521`. | Acquired but not analyzed until a state-pair mapping is frozen. |

## Evidence captured locally

- `data/metadata/weargait-synapse-entity.json`
- `data/metadata/weargait-synapse-wiki.json`
- `data/metadata/weargait-access-wiki.json`
- `data/metadata/carepd-dataverse-api.json`
- `data/metadata/carepd-hf-api.json`
- `data/metadata/CARE-PD-README.md`

Run `python3 scripts/acquire_dataset_metadata.py` to refresh these metadata snapshots and write `data/metadata/manifest.json` with retrieval timestamps and SHA-256 hashes. The script intentionally does not log in, request access, accept click-through terms, or download participant-level files.

## Reproduction gate

Keep the authorized Drive folder outside the repository, set `PARKINSON_GAIT_DATA_ROOT` to it, and run `bash scripts/reproduce_final_results.sh`. The run writes row-level audit files locally under `results/` (ignored by Git) and a public-safe aggregate manifest under `results/frozen/results.json`. Keep WearGait and CARE-PD identifiers separate.

## Citations and links

- FDA WearGait-PD: <https://cdrh-rst.fda.gov/weargait-pd-wearables-dataset-gait-parkinsons-disease-and-age-matched-controls>
- FDA WearGait-PD Longitudinal: <https://cdrh-rst.fda.gov/weargait-pd-longitudinal-multi-session-wearables-dataset-gait-parkinsons-disease>
- WearGait-PD paper: <https://doi.org/10.1038/s41597-026-06806-2>
- CARE-PD code and download pointers: <https://github.com/TaatiTeam/CARE-PD>
- CARE-PD Dataverse record: <https://doi.org/10.5683/SP3/TWIKMK>
