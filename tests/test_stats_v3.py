import unittest

import numpy as np
import pandas as pd

from src.stats_v3 import gee_raw_effect, icc_2_1


class TestICCA1(unittest.TestCase):
    def test_uses_session_mean_square_for_absolute_agreement(self):
        values = np.array([[1., 3.], [2., 4.], [3., 5.], [4., 6.]])
        icc, mse = icc_2_1(values)
        # The fixed two-unit session offset is penalized by ICC(A,1), unlike
        # a consistency-only coefficient.  The expected value is from the
        # explicit two-way absolute-agreement mean-square formula.
        self.assertTrue(np.isclose(icc, 5 / 11))
        self.assertTrue(np.isclose(mse, 0.0))

    def test_raw_effect_returns_native_unit_columns(self):
        rows = [{"participant_id": person, "mds_updrs_gait_item": person % 5,
                 "age": 60 + person, "height_m": 1.7, "sex": "F",
                 "task": task, "site": "A", "cadence": 100 + person}
                for person in range(25) for task in ("SP", "HP")]
        result = gee_raw_effect(pd.DataFrame(rows), "cadence")
        self.assertEqual(result["raw_effect_status"], "OK")
