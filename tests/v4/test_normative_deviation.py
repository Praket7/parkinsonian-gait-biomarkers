import pandas as pd
from src.v4.normative_deviation import fit_controls, score
def test_controls_only_model():
 c=pd.DataFrame({"clinical_cohort":["control"]*6,"age":range(6),"height_m":[1.7]*6,"x":range(6)})
 assert len(score(c,fit_controls(c,["x"]))) == 6
