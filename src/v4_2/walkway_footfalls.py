"""Conservative raw contact parser, used only after a metric geometry gate."""
from __future__ import annotations
import numpy as np
import pandas as pd

def parse_time(values): return pd.to_numeric(pd.Series(values).astype(str).str.replace(" sec","",regex=False),errors="coerce")
def initial_contacts(table: pd.DataFrame) -> pd.DataFrame:
    time=parse_time(table["Time"]); rows=[]
    for foot,column in (("L","L Foot Contact"),("R","R Foot Contact")):
        contact=pd.to_numeric(table[column],errors="coerce").fillna(0).gt(0)
        for index in np.flatnonzero(contact.to_numpy() & ~contact.shift(fill_value=False).to_numpy()): rows.append({"foot":foot,"time":float(time.iloc[index])})
    result=pd.DataFrame(rows).sort_values("time").reset_index(drop=True) if rows else pd.DataFrame(columns=["foot","time"])
    if result.time.duplicated().any() or result.time.diff().dropna().le(0).any(): raise ValueError("duplicated or nonmonotonic contacts")
    return result
