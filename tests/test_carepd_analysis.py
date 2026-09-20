import unittest

import numpy as np

from src.carepd_analysis import safe_aggregate, translation_speed_sensitivities


class CarePDAnalysisTests(unittest.TestCase):
    def test_canonical_z_speed_sensitivities(self):
        record = {"trans": np.c_[np.zeros((5, 2)), np.arange(5) / 2], "fps": 2}
        result = translation_speed_sensitivities(record)
        self.assertAlmostEqual(result["endpoint_z_speed_m_s"], 1.0)
        self.assertAlmostEqual(result["framewise_z_speed_m_s"], 1.0)
        self.assertAlmostEqual(result["slope_z_speed_m_s"], 1.0)

    def test_aggregate_has_no_row_identifiers_and_reports_cohort(self):
        trans = np.c_[np.zeros((10, 2)), np.arange(10) / 10]
        raw = {"3DGait": {f"person-{i}": {"walk": {
            "trans": trans, "fps": 10, "UPDRS_GAIT": i % 3, "medication": None
        }} for i in range(8)}}
        result = safe_aggregate(raw, min_participants=3)
        self.assertIn("cohort", result)
        self.assertIn("endpoint_z_speed_m_s", set(result.outcome))
        self.assertNotIn("participant_key", result.columns)
        self.assertNotIn("trial", result.columns)

    def test_bmclab_state_sensitivity_is_conditional(self):
        trans = np.c_[np.zeros((10, 2)), np.arange(10) / 10]
        raw = {"BMCLab": {f"person-{i}": {"walk": {
            "trans": trans, "fps": 10, "UPDRS_GAIT": i % 3,
            "medication": "on" if i % 2 else "off"
        }} for i in range(8)}}
        result = safe_aggregate(raw, min_participants=3)
        self.assertTrue(any(result.outcome.str.endswith("_on")))
        self.assertTrue(any(result.outcome.str.endswith("_off")))


if __name__ == "__main__":
    unittest.main()
