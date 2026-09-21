"""Create an explicit v4 evidence matrix from aggregate analysis tables."""
from __future__ import annotations
import pandas as pd
from .qualification import evidence_row


def build_evidence(associations, definitions, reliability=None, robustness=None):
    reliability = reliability if reliability is not None else pd.DataFrame()
    rows = []
    for _, result in associations.iterrows():
        feature = result["feature"]; meta = definitions.get(feature, {})
        rel = reliability[reliability.feature.eq(feature)] if not reliability.empty and "feature" in reliability else pd.DataFrame()
        icc = rel.icc_2_1.max() if not rel.empty and "icc_2_1" in rel else float("nan")
        rows.append(evidence_row(feature, result, family=meta.get("construct", "unknown"), speed_construct=meta.get("speed_construct", "requires_speed_adjustment"), reliability=icc))
    return pd.DataFrame(rows)
