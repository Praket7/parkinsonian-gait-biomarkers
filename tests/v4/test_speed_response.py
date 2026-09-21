import pandas as pd
from src.v4.speed_response import response_indices
def test_speed_response():
 d=pd.DataFrame({"participant_id":["p","p"],"task":["SP","HP"],"gait_speed":[1,1.2],"stride_length_mean":[1,1.1],"cadence":[100,110]})
 assert response_indices(d).stride_scaling_response_v1.notna().all()
