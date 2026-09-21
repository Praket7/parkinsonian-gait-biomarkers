import unittest

import numpy as np

from src.carepd_analysis import matched_temporal_aggregate, safe_aggregate, translation_speed_sensitivities
from src.carepd_h36m import extract_features


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

    def test_matched_temporal_layer_fails_safe_without_canonical_events(self):
        raw = {"3DGait": {"person": {"walk": {
            "pose": np.zeros((20, 72)), "trans": np.zeros((20, 3)), "fps": 30
        }}}}
        result = matched_temporal_aggregate(raw, min_participants=1)
        self.assertEqual(set(result.status), {"NOT_ESTIMABLE"})
        self.assertTrue((result.n_trials == 0).all())
        self.assertTrue(result.estimability_reason.str.contains("official_h36m").all())

    def test_care_known_cadence_step_time_length_and_spacing(self):
        frames, fps = 121, 30
        joints = np.zeros((frames, 17, 3))
        joints[:, 0, 2] = np.arange(frames) / fps
        for event in (15, 45, 75, 105):
            joints[event, 3, 0], joints[event, 6, 0] = -.2, .2
        result = extract_features(joints, fps)
        self.assertEqual(result["status"], "OK")
        self.assertAlmostEqual(result["step_time_mean"], 1.0)
        self.assertAlmostEqual(result["cadence"], 60.0)
        self.assertAlmostEqual(result["step_length_mean"], 1.0)


if __name__ == "__main__":
    unittest.main()
