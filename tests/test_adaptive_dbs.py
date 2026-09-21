import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.adaptive_dbs import audit, paired_states, to_canonical


class AdaptiveDBSAdapterTests(unittest.TestCase):
    def test_audit_reports_archive_as_source_member(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "release.zip").write_bytes(b"archive placeholder")
            result = audit(root)
            self.assertEqual(result["status"], "OK")
            self.assertTrue(result["source_members_are_not_published"])

    def test_paired_states_uses_only_matched_participants(self):
        table = pd.DataFrame({"participant_key": ["p1", "p1", "p2", "p2", "p3"], "dbs_state": ["off", "on", "off", "on", "off"], "speed": [1.0, 1.4, 0.8, 1.0, 1.1]})
        result = paired_states(table, "speed", state_a="off", state_b="on")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["n_participants"], 2)
        self.assertAlmostEqual(result["mean_paired_change"], 0.3)

    def test_ambiguous_more_than_two_states_is_not_estimable(self):
        table = pd.DataFrame({"participant_key": ["p1", "p1", "p1"], "dbs_state": ["off", "on", "ramp"], "speed": [1.0, 1.2, 1.1]})
        result = paired_states(table, "speed")
        self.assertEqual(result["status"], "NOT_ESTIMABLE")
        self.assertEqual(result["reason"], "EXPECTED_EXACTLY_TWO_STATES")

    def test_mapping_requires_state_and_namespaces_participant(self):
        table = pd.DataFrame({"subject": [7], "trial": [1], "stim": ["off"]})
        result = to_canonical(table, {"subject": "participant_key", "trial": "visit_id", "stim": "dbs_state"})
        self.assertTrue(result.loc[0, "participant_key"].startswith("adaptive_dbs:"))

    def test_missing_state_mapping_fails_closed(self):
        with self.assertRaises(ValueError):
            to_canonical(pd.DataFrame({"subject": [7], "trial": [1]}), {"subject": "participant_key", "trial": "visit_id"})
