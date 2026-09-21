import pandas as pd
from src.v4.mobilised_stability import stability_selection
def test_stability():
 d=pd.DataFrame({"participant_key":[str(x) for x in range(20)],"mdsscore3":range(20),"gait_speed":range(20)})
 assert stability_selection(d,["gait_speed"],iterations=5).status.iloc[0] == "OK"
