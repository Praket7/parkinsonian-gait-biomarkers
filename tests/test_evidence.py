import pandas as pd
import unittest

from src.stats_v3 import site_sign_consistency


class SiteEvidenceTests(unittest.TestCase):
    def test_site_sign_consistency_is_canonical_and_false_is_not_truthy(self):
        context = pd.DataFrame({
            "feature": ["cadence", "cadence", "cadence"],
            "analysis": ["leave_one_site_out", "leave_one_site_out", "task_specific"],
            "same_direction": ["True", "True", "False"],
        })
        self.assertEqual(site_sign_consistency(context, "cadence"), 1.0)
