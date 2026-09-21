import unittest
import numpy as np
import pandas as pd

from src.longitudinal_stats import measurement_error, paired_change_summary, within_between_decomposition


class LongitudinalStatsTests(unittest.TestCase):
    def test_within_between_separates_person_means(self):
        frame = pd.DataFrame({"participant_key":["a","a","b","b"],"anchor":[0,2,10,12]})
        result = within_between_decomposition(frame,"anchor")
        self.assertEqual(result.anchor_between.tolist(), [1,1,11,11])
        self.assertEqual(result.anchor_within.tolist(), [-1,1,-1,1])

    def test_measurement_error_and_change_are_explicit(self):
        frame = pd.DataFrame({"participant_key":list("abcde")*2,"visit_order":[0]*5+[1]*5,"feature":[0]*5+[2]*5})
        row=measurement_error(frame,"feature")
        self.assertEqual(row["status"],"OK")
        self.assertEqual(row["proportion_exceeding_mdc95"], 0)

    def test_small_paired_data_not_estimable(self):
        frame=pd.DataFrame({"participant_key":["a"],"visit_order":[0],"f":[1],"a":[1]})
        self.assertEqual(paired_change_summary(frame,"f","a")["status"],"NOT_ESTIMABLE")
