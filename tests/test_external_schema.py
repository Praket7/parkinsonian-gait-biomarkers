import unittest
import pandas as pd

from src.external_schema import CANONICAL_COLUMNS, canonicalize, namespaced_key, public_aggregate


class ExternalSchemaTests(unittest.TestCase):
    def test_namespaces_source_keys(self):
        self.assertNotEqual(namespaced_key("mendeley", "7"), namespaced_key("mobilised", "7"))

    def test_duplicate_visit_fails_closed(self):
        table = pd.DataFrame({"participant_key":["a", "a"], "visit_id":["v1", "v1"]})
        with self.assertRaises(ValueError): canonicalize(table, "synthetic")

    def test_missing_fields_remain_missing(self):
        result = canonicalize(pd.DataFrame({"participant_key":["a"], "visit_id":["v1"]}), "synthetic")
        self.assertEqual(list(result.columns), CANONICAL_COLUMNS)
        self.assertTrue(result.gait_speed.isna().all())

    def test_public_identity_column_rejected(self):
        with self.assertRaises(ValueError): public_aggregate(pd.DataFrame({"participant_id":["x"]}))
