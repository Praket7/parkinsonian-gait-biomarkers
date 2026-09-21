import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

from src.mobilised_cvs import (audit, convert_units, filter_reliable_week,
                               resolve_anchor, to_canonical)


class MobilisedTests(unittest.TestCase):
    def test_exact_anchor_beats_part_three(self):
        self.assertEqual(resolve_anchor(["MDS_UPDRS_III", "MDS_UPDRS_3_10"]), ("MDS_UPDRS_3_10", "exact"))

    def test_anchor_hierarchy_is_explicit(self):
        self.assertEqual(resolve_anchor(["PIGD_total"])[1], "construct_level")
        self.assertEqual(resolve_anchor(["MDS_UPDRS_III"])[1], "broad_motor")
        self.assertEqual(resolve_anchor(["age"])[1], "ANCHOR_UNAVAILABLE")

    def test_duplicate_participant_visit_rejected(self):
        table = pd.DataFrame({"pid": ["a", "a"], "visit": ["t1", "t1"], "order": [1, 1], "speed": [1., 2.]})
        with self.assertRaises(ValueError):
            to_canonical(table, {"pid": "participant_key", "visit": "visit_id", "order": "visit_order", "speed": "gait_speed"})

    def test_namespaced_ids_and_visit_order_are_preserved(self):
        table = pd.DataFrame({"pid": [7, 7], "visit": ["t1", "t2"], "order": [1, 2], "speed": [3.6, 7.2]})
        result = to_canonical(table, {"pid": "participant_key", "visit": "visit_id", "order": "visit_order", "speed": "gait_speed"}, units={"gait_speed": ("km/h", "m/s")})
        self.assertTrue(result.participant_key.iloc[0].startswith("mobilised_cvs:"))
        self.assertEqual(result.visit_order.tolist(), [1, 2])
        self.assertEqual(result.gait_speed.tolist(), [1., 2.])

    def test_unit_conversion_is_fail_closed(self):
        self.assertEqual(convert_units(pd.Series([100.]), "cm", "m").iloc[0], 1.)
        with self.assertRaises(ValueError):
            convert_units(pd.Series([1.]), "furlongs", "m")

    def test_reliable_week_primary_and_sensitivity(self):
        table = pd.DataFrame({"reliable_week_status": ["PASS", "FAIL", None], "speed": [1, 2, 3]})
        self.assertEqual(filter_reliable_week(table).speed.tolist(), [1])
        self.assertEqual(len(filter_reliable_week(table, sensitivity=True)), 3)

    def test_schema_audit_reads_headers_from_nested_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inner = root / "Walking Bout DMO Data.zip"
            payload = b"participantid,visit_number,averagestridespeed,averagecadence\n1,t1,1.0,90\n"
            nested = root / "nested.csv"
            nested.write_bytes(payload)
            with zipfile.ZipFile(inner, "w") as archive:
                archive.write(nested, "CVS-T1-wb-dmo.csv")
            result = audit(root)
            self.assertEqual(result["schema"]["participant_identifier_fields"], ["participantid"])
            self.assertIn("averagestridespeed", result["schema"]["dmo_fields"])
            self.assertEqual(result["status"], "NOT_ESTIMABLE_SOURCE_COMPONENT_MISSING")

    def test_missing_release_is_not_estimable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = audit(Path(directory))
            self.assertEqual(result["status"], "NOT_ESTIMABLE_SOURCE_COMPONENT_MISSING")
            self.assertFalse(result["source_members"])


if __name__ == "__main__":
    unittest.main()
