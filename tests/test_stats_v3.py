import unittest

import numpy as np

from src.stats_v3 import icc_2_1


class TestICCA1(unittest.TestCase):
    def test_uses_session_mean_square_for_absolute_agreement(self):
        values = np.array([[1., 3.], [2., 4.], [3., 5.], [4., 6.]])
        icc, mse = icc_2_1(values)
        # The fixed two-unit session offset is penalized by ICC(A,1), unlike
        # a consistency-only coefficient.  The expected value is from the
        # explicit two-way absolute-agreement mean-square formula.
        self.assertTrue(np.isclose(icc, 5 / 11))
        self.assertTrue(np.isclose(mse, 0.0))
