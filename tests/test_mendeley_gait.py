import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.mendeley_gait import audit, collapse_bilateral, to_canonical


class MendeleyAdapterTests(unittest.TestCase):
    def test_audit_discovers_archive_tables_without_opening_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "release.zip").write_bytes(b"not a zip")
            (root / "README.pdf").write_bytes(b"metadata")
            result = audit(root)
            self.assertEqual(result["status"], "OK")
            self.assertEqual(result["candidate_tables"], [])
            self.assertTrue(result["mapping_required"])

    def test_collapse_bilateral_is_participant_visit_aware(self):
        table = pd.DataFrame({"pid": ["p1", "p1", "p2"], "visit": [1, 1, 1], "side": ["L", "R", "L"], "speed": [1.0, 3.0, 2.0]})
        result = collapse_bilateral(table, "pid", "visit", "side")
        self.assertEqual(result.loc[result.pid == "p1", "speed"].iloc[0], 2.0)
        self.assertEqual(result.loc[result.pid == "p1", "source_record_count"].iloc[0], 2)

    def test_mapping_is_explicit_and_namespaced(self):
        table = pd.DataFrame({"subject": [7], "session": ["baseline"], "gait_speed": [1.2]})
        result = to_canonical(table, {"subject": "participant_key", "session": "visit_id", "gait_speed": "gait_speed"})
        self.assertEqual(result.loc[0, "dataset"], "mendeley_gait")
        self.assertTrue(result.loc[0, "participant_key"].startswith("mendeley:"))

    def test_missing_mapping_fails_closed(self):
        with self.assertRaises(ValueError):
            to_canonical(pd.DataFrame({"subject": [7]}), {"subject": "participant_key"})
