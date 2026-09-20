# Data access record

Accessed 2026-09-20. The complete machine-readable evidence is under
`data/metadata/manifest.json`; its public snapshots carry SHA-256 values.

| Dataset | Source | Version/license status | Local status |
| --- | --- | --- | --- |
| WearGait-PD | FDA record; Synapse `syn52540892` | CC BY 4.0 metadata; registered Synapse access/terms required for participant files | Authorized copy used from controlled external Drive storage; never committed |
| WearGait-PD Longitudinal | FDA record; Synapse `syn74686228` | Same project access route | Authorized copy used from controlled external Drive storage; never committed |
| CARE-PD | Borealis `10.5683/SP3/TWIKMK`; `vida-adl/CARE-PD` | CC BY-NC-ND 4.0 reported; project terms must be reviewed before use | Authorized copy used from controlled external Drive storage; never committed |

No data-access terms were accepted by automation, and no participant-level
file may be redistributed through this repository. The authorized v3 run used
the controlled copies and published only aggregate results, figures, and hashes.

The longitudinal release was also audited with
`python scripts/audit_longitudinal_schema.py`. MATLAB files are inspected with
`scipy.io.whosmat`; HDF5/MATLAB 7.3 files are traversed with `h5py` names,
shapes, dtypes, and attribute names only. Synapse entity/wiki snapshots under
`data/metadata/` are searched for metadata references only. No signal arrays,
table rows, or participant values are emitted. When no single schema or
metadata record contains a participant/subject key, session/visit key, and
clinical-score key together, the frozen status is
`NOT_ESTIMABLE_AFTER_ARCHIVE_AND_SCHEMA_AUDIT`; this is an unavailable
estimand, not evidence that longitudinal validity failed.
