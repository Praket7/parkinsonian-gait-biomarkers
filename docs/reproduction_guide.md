# Reproduction guide

This guide separates checks that need only public files from analyses that need approved participant data. Run commands from the repository root. Python 3.11 is the supported environment in the current continuous integration workflow.

## Prepare the environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
bash scripts/setup_environment.sh
pytest -q
```

The setup script installs the pinned analysis dependencies, pytest, plus this project in editable mode. The full test suite is pytest. Python unittest discovery alone does not include every test.

## Refresh public metadata

```bash
python scripts/acquire_dataset_metadata.py
```

This refreshes public source descriptions. It does not sign in, accept dataset terms, request access, or download participant files.

## Run the main pipeline

Set `PARKINSON_GAIT_DATA_ROOT` to an authorized directory containing the folders listed in [the dataset guide](../DATASETS.md). Keep raw files outside Git. The main pipeline writes local row level records under ignored result folders. Do not publish these records.

```bash
export PARKINSON_GAIT_DATA_ROOT="/path/to/authorized/Parkinsonian_Gait_Data"
bash scripts/reproduce_final_results.sh
```

The main pipeline reproduces the original analysis. It does not by itself rebuild the later v4.3, v4.4, or v4.5 results.

## Rebuild the v4.5 correction

The later analysis has ordered dependencies.

1. Rebuild the eight walkway measurements from WearGait V1. All eight must pass the frozen comparison rule.
2. Apply the frozen v4.1 score to longitudinal records. This step does not refit the model.
3. Run the v4.4 measurement protocol after the v4.3 files exist.
4. Run the v4.5 correction after the v4.4 outputs exist.
5. Audit authorized source files, regenerate the report, then run the release gate plus history check.

```bash
export PARKINSON_GAIT_DATA_ROOT="/path/to/authorized/Parkinsonian_Gait_Data"
export V1_ROOT="$PARKINSON_GAIT_DATA_ROOT/WearGait_PD_V1"
export LONGITUDINAL_ROOT="$PARKINSON_GAIT_DATA_ROOT/WearGait_PD_Longitudinal"

PYTHONPATH=. python scripts/run_v4_3_v1_equivalence.py --v1-root "$V1_ROOT"
PYTHONPATH=. python scripts/run_v4_3_h4_longitudinal.py --v1-root "$V1_ROOT" --longitudinal-root "$LONGITUDINAL_ROOT"
PYTHONPATH=. python scripts/run_v4_4_measurement_protocol.py --v1-root "$V1_ROOT" --longitudinal-root "$LONGITUDINAL_ROOT"
PYTHONPATH=. python scripts/run_v4_5_repair.py --v1-root "$V1_ROOT"
PYTHONPATH=. python scripts/audit_v4_5_sources.py --data-root "$PARKINSON_GAIT_DATA_ROOT" --hydrate-unreadable
PYTHONPATH=. python scripts/generate_v4_5_report.py
python scripts/qa_release_gate.py
python scripts/check_analysis_freeze.py
```

The source audit may request temporary Synapse copies when a Drive entry is only a cloud placeholder. It uses a temporary Synapse cache, then removes that temporary folder when the script completes. It needs existing authorized access. It does not bypass terms or permissions. A slow cloud placeholder may time out during the first read. Use the hydration option only when Synapse access is already approved. A failed download, stale credential, missing folder, or disk limit means the reproduction is incomplete. It is not a negative scientific result.

The freeze check verifies ancestry against the project history. A shallow clone can fail that check. Fetch the complete history before diagnosing the analysis itself.

```bash
git fetch --unshallow
```

A Git tag identifies a commit. A GitHub Release is a separate publication record. At the time of the September 2026 audit, v4.5.1 was a tag while the newest GitHub Release page still named v3.1.0. Check both when recording the release state.

## Common setup interruptions

An import error usually means the virtual environment was not activated or the setup script did not finish. A missing folder points to an incorrect `PARKINSON_GAIT_DATA_ROOT` value or a source folder that is not available locally. A cloud file timeout means the local Drive entry did not open promptly. The authorized Synapse hydration option can retry that file. Synapse sign in errors require account access to be restored. A disk space error requires more free space on the machine running the analysis. These are reproduction blockers, not scientific outcomes.

## Public verification boundaries

Continuous integration runs the test suite, the release gate, the history check, plus the public pipeline. It does not access authorized participant records. A green workflow proves that those checks passed. It does not prove the full private data analysis was rerun.

The report values in this repository were checked against the frozen aggregate outputs. The September 2026 audit did not rerun the full authorized participant level analysis. Keep that distinction in any paper, poster, or presentation.
