import pickle
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.carepd import infer_trial_context, read_carepd_directory, read_carepd_pickle


class CarePDTests(unittest.TestCase):
    def test_nested_pickle_metadata_preserves_raw_arrays(self):
        record = {"pose": np.zeros((4, 72), dtype=np.float32), "trans": np.zeros((4, 3)),
                  "fps": 30, "UPDRS_GAIT": 2, "medication": "off", "other": None}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BMCLab.pkl"
            with path.open("wb") as stream:
                pickle.dump({"SUB01": {"SUB01_off_walk_1": record}}, stream)
            raw, table = read_carepd_pickle(path)
        self.assertEqual(raw["SUB01"]["SUB01_off_walk_1"]["pose"].shape, (4, 72))
        self.assertEqual(table.loc[0, "cohort"], "BMCLab")
        self.assertEqual(table.loc[0, "n_frames"], 4)
        self.assertEqual(table.loc[0, "mds_updrs_gait_item"], 2)

    def test_directory_excludes_folds_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = {"pose": np.zeros((1, 72)), "trans": np.zeros((1, 3)), "fps": 25,
                      "UPDRS_GAIT": 0, "medication": None, "other": None}
            with (root / "3DGait.pkl").open("wb") as stream:
                pickle.dump({0: {"trial": record}}, stream)
            self.assertEqual(len(read_carepd_directory(root)), 1)

    def test_context_inference_is_conservative(self):
        self.assertEqual(infer_trial_context("SUB01_off_walk_1"), {"medication_from_id": "off", "walk_label": "walk"})
        self.assertEqual(infer_trial_context("vid0073_0055"), {"medication_from_id": None, "walk_label": None})


if __name__ == "__main__":
    unittest.main()
