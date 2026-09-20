import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from src.features import extract_bout_features
from src.io import canonical_task, derive_site, load_csv_bouts
from src.run_pipeline import _feature_table, _primary_severity, run
from src.stats import _design, bh_fdr
from src.weargait import load_weargait_csv_bouts, read_weargait_csv
from src.weargait_clinical import join_clinical_features, load_v1_clinical


class PipelineTests(unittest.TestCase):
    def test_event_features(self):
        f = extract_bout_features({"left_contacts": [0, 2], "right_contacts": [1, 3]})
        self.assertAlmostEqual(f["cadence"], 60.0)
        self.assertAlmostEqual(f["step_time_mean"], 1.0)

    def test_site_mapping(self):
        self.assertEqual(derive_site("NLS001"), "Johns_Hopkins_Outpatient")
        self.assertEqual(derive_site("unmapped"), "unknown")

    def test_task_alias_and_covariates_survive_aggregation(self):
        self.assertEqual(canonical_task("FreeWalk"), "FW")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bouts.csv"
            pd.DataFrame({
                "participant_id": ["NLS001"], "task": ["SP"], "cadence": [60],
                "med_state": ["ON"], "time_since_med": [2.0],
                "disease_duration_years": [4.0], "dbs": [False],
            }).to_csv(path, index=False)
            raw = load_csv_bouts(tmp)
        table = _feature_table(raw)
        self.assertEqual(table.loc[0, "medication_state"], "ON")
        self.assertEqual(table.loc[0, "disease_duration"], 4.0)
        self.assertFalse(table.loc[0, "dbs_status"])

    def test_primary_severity_requires_nonmissing_observations(self):
        table = pd.DataFrame({"mds_updrs_gait_item": [np.nan] * 12, "mds_updrs_iii": list(range(12))})
        self.assertEqual(_primary_severity(table), "mds_updrs_iii")

    def test_speed_is_not_a_covariate_when_speed_is_outcome(self):
        frame = pd.DataFrame({"gait_speed": [1, 2], "age": [60, 61], "task": ["SP", "HP"]})
        _, names = _design(frame, "gait_speed")
        self.assertNotIn("gait_speed", names[2:])

    def test_pipeline_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            pd.DataFrame({
                "participant_id": ["NLS001", "NLS001", "HC002"],
                "task": ["SP", "SP", "HP"],
                "cadence": [60, 62, 55],
                "gait_speed": [1.0, 1.1, 0.8],
            }).to_csv(root / "data" / "bouts.csv", index=False)
            cfg = root / "analysis.yaml"
            cfg.write_text("""seed: 1\nprimary_tasks: [SP]\ncontext_tasks: [HP]\ndata:\n  input_dir: %s\n  output_dir: %s\n""" % (root / "data", root / "results"))
            result = run(cfg)
            self.assertEqual(result["primary_n_participants"], 2)
            self.assertTrue((root / "results" / "frozen" / "results.json").exists())
            self.assertEqual(json.loads((root / "results" / "frozen" / "results.json").read_text())["status"], "feature_table_ready")

    def test_fdr_is_monotone_in_sorted_order(self):
        adjusted = bh_fdr(pd.Series([0.01, 0.04, 0.03])).sort_values().to_numpy()
        self.assertTrue(np.all(np.diff(adjusted) >= 0))

    def test_weargait_signal_csv_ingestion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frame = pd.DataFrame({
                "Time": [f"{i / 10:g} sec" for i in range(80)],
                "L Foot Contact": [1 if i in (10, 30, 50, 70) else 0 for i in range(80)],
                "R Foot Contact": [1 if i in (20, 40, 60) else 0 for i in range(80)],
                "irrelevant": range(80),
            })
            path = root / "NLS001_FreeWalk.csv"
            frame.to_csv(path, index=False)
            row = read_weargait_csv(path)
            rejected = read_weargait_csv(path, minimum_clean_walk_seconds=10)
            table = load_weargait_csv_bouts(root)
        self.assertEqual(row["participant_id"], "NLS001")
        self.assertEqual(row["task"], "FW")
        self.assertAlmostEqual(row["step_time_mean"], 1.0, places=6)
        self.assertTrue(row["qc_valid"])
        self.assertFalse(rejected["qc_valid"])
        self.assertIn("short_clean_bout", rejected["qc_reason"])
        self.assertEqual(len(table), 1)

    def test_v1_clinical_header_units_and_id_join(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pd_path = root / "PD - Demographic+Clinical - datasetV1.csv"
            pd.DataFrame({
                "Subject ID": ["NLS001"], "Height (in)": [60], "Age (years)": [70],
                "Sex": ["Female"], "Years since PD diagnosis": [4], "DBS?": ["No"],
                "3b": ["ON"],
                "Time of research session": ["12:30 PM"], "Time of last medication dose": ["8:00 AM"],
                "MDSUPDRS_3-1": [1], "MDSUPDRS_3-2": [2], "MDSUPDRS_3-3-Neck": [1],
                "MDSUPDRS_3-3-RUE": [2], "MDSUPDRS_3-3-LUE": [3], "MDSUPDRS_3-10": [2],
            }).to_csv(pd_path, index=False)
            # Real exports have one explanatory row above the header.
            text = pd_path.read_text()
            pd_path.write_text("WearGait explanatory row\n" + text)
            clinical = load_v1_clinical(pd_path)
            joined = join_clinical_features(pd.DataFrame({"participant_id": ["NLS001", "OTHER"], "cadence": [100, 90]}), clinical)
        self.assertAlmostEqual(clinical.loc[0, "height_m"], 1.524)
        self.assertEqual(clinical.loc[0, "mds_updrs_gait_item"], 2)
        self.assertEqual(clinical.loc[0, "mds_updrs_iii"], 11)
        self.assertAlmostEqual(clinical.loc[0, "time_since_medication"], 4.5)
        self.assertEqual(clinical.loc[0, "medication_state"], "on")
        self.assertTrue(pd.isna(joined.loc[1, "age"]))


if __name__ == "__main__":
    unittest.main()
