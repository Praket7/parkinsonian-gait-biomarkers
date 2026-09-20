import unittest

import pandas as pd

from scripts.audit_longitudinal_clinical_files import audit_archive
from scripts.audit_longitudinal_schema import audit_archive as audit_schema_archive
from src.longitudinal import icc_2_1, prepare_two_session_reliability, reliability_qc


class LongitudinalTests(unittest.TestCase):
    def test_task_specific_two_session_table_and_qc(self):
        frame = pd.DataFrame({
            "participant_id": ["A", "A", "A", "B", "B", "B"],
            "task": ["SP", "SP", "HP", "SP", "SP", "SP"],
            "session": ["s1", "s2", "s1", "s1", "s2", "s2"],
            "cadence": [60, 62, 70, 55, 56, 57],
        })
        table = prepare_two_session_reliability(frame, ["cadence"])
        self.assertEqual(set(table["participant_id"]), {"A", "B"})
        self.assertEqual(set(table["task"]), {"SP"})
        self.assertEqual(reliability_qc(table, ["cadence"])["complete_feature_rows"], 2)

    def test_icc_two_way_absolute_agreement(self):
        self.assertGreater(icc_2_1([[1, 1], [2, 2], [3, 3], [4, 4]]), 0.99)

    def test_archive_audit_exposes_headers_not_values(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "NLS001s1.csv"
            path.write_text("Subject ID,UPDRS score\nNLS001,4\n")
            row = audit_archive(tmp, max_hash_bytes=10000)[0]
        self.assertEqual(row["header_keyword_hits"], "score|subject|updrs")
        self.assertNotIn("NLS001,4", str(row))

    def test_schema_audit_does_not_read_mat_values_and_freezes_status(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signals.mat"
            path.write_bytes(b"not-a-mat-payload")
            report = audit_schema_archive(tmp)
        self.assertEqual(report["longitudinal_clinical_status"], "NOT_ESTIMABLE_AFTER_ARCHIVE_AND_SCHEMA_AUDIT")
        self.assertFalse(report["joinable_participant_session_clinical_schema"])


if __name__ == "__main__":
    unittest.main()
