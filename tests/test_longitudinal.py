import unittest

import pandas as pd

from scripts.audit_longitudinal_clinical_files import audit_archive
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


if __name__ == "__main__":
    unittest.main()
