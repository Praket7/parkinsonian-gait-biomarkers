import pandas as pd
from src.v4_2.walkway_footfalls import initial_contacts
from src.v4_2.walkway_metrics import summarize_contacts
def test_synthetic_footfalls():
    table=pd.DataFrame({'Time':['0 sec','.5 sec','1 sec','1.5 sec','2 sec'],'L Foot Contact':[1,0,1,0,1],'R Foot Contact':[0,1,0,1,0]})
    result=summarize_contacts(initial_contacts(table))
    assert result['step_time_mean']==.5 and result['stride_time_mean']==1 and result['cadence']==120
