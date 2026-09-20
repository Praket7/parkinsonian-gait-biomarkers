import pickle
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.carepd_speed import speed_from_pickle


class CarePDSpeedTests(unittest.TestCase):
    def test_global_translation_speed_and_metadata(self):
        record = {"pose": np.zeros((5, 72)), "trans": np.array([[0., 0., 0.], [1., 0., 0.], [2., 0., 0.], [3., 0., 0.], [4., 0., 0.]]),
                  "fps": 2, "UPDRS_GAIT": 1, "medication": "off", "other": None}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "BMCLab.pkl"
            with path.open("wb") as stream:
                pickle.dump({"SUB01": {"trial": record}}, stream)
            table = speed_from_pickle(path)
        self.assertEqual(table.loc[0, "speed_axis"], 0)
        self.assertAlmostEqual(table.loc[0, "duration_s"], 2.0)
        self.assertAlmostEqual(table.loc[0, "global_forward_speed_m_s"], 2.0)
        self.assertEqual(table.loc[0, "mds_updrs_gait_item"], 1)


if __name__ == "__main__":
    unittest.main()
