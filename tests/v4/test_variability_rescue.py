from src.v4.variability_rescue import choose_minimum_cycles, longbout_variability
import numpy as np
def test_longbout_and_convergence():
 assert np.isfinite(longbout_variability(np.arange(0,40,.8),np.arange(.4,40,.8),minimum_cycles=20)["step_time_cv_longbout_v1"])
 assert choose_minimum_cycles([{"n_cycles":30,"relative_error":.05}]) == 30
