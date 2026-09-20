import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from src.features import extract_bout_features
from src.io import derive_site
from src.run_pipeline import run
from src.stats import bh_fdr


class PipelineTests(unittest.TestCase):
    def test_event_features(self):
        f = extract_bout_features({"left_contacts": [0, 2], "right_contacts": [1, 3]})
        self.assertAlmostEqual(f["cadence"], 60.0)
        self.assertAlmostEqual(f["step_time_mean"], 1.0)

    def test_site_mapping(self):
        self.assertEqual(derive_site("NLS001"), "Johns_Hopkins_Outpatient")
        self.assertEqual(derive_site("unmapped"), "unknown")

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


if __name__ == "__main__":
    unittest.main()
