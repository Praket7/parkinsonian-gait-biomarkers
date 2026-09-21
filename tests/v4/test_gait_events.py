import numpy as np
from src.v4.gait_events import event_qc
def test_alternating_events_pass_cycle_qc(): assert event_qc(np.arange(0,40,.8),np.arange(.4,40,.8),minimum_cycles=20)["status"] == "OK"
