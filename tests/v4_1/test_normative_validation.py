import numpy as np
import pandas as pd
import pytest
from src.v4_1.normative import FEATURES, fit_reference, score, serialize
from src.v4_1.validation import grouped_folds

def controls():
    rng=np.random.default_rng(4); rows=[]
    for person in range(10):
        for task in range(2):
            rows.append({"participant_id":str(person),"clinical_cohort":"control","age":60+person,"height_m":1.6+.01*person,**dict(zip(FEATURES,rng.normal(size=8)))})
    return pd.DataFrame(rows)
def test_reference_rejects_pd_rows():
    table=controls(); table.loc[0,"clinical_cohort"]="pd"
    with pytest.raises(ValueError): fit_reference(table)
def test_roundtrip_score_and_group_folds():
    table=controls(); model=fit_reference(table); restored=serialize(model); restored["features"]=restored["feature_order"]
    assert np.max(np.abs(score(table,model)-score(table,restored))) == 0
    for train,test in grouped_folds(table,"participant_id",5):
        assert set(table.iloc[train].participant_id).isdisjoint(set(table.iloc[test].participant_id))
