#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import pandas as pd


def main():
    root=Path("results/v4/frozen"); evidence=pd.read_csv(root/"evidence_matrix.csv") if (root/"evidence_matrix.csv").exists() else pd.DataFrame()
    lines=["# When Association Is Not Validation", "", "## Prospective v4 biomarker-redesign extension", "", "v4 is a separately frozen prospective extension; it does not alter the v3.2.4 conclusion that 0/11 original conventional features qualified.", "", "## Evidence matrix"]
    lines += ["No v4 clinical result is available."] if evidence.empty else ["```csv", evidence.to_csv(index=False).strip(), "```"]
    lines += ["", "## Interpretation", "A candidate is useful only in its declared context of use. `NOT_ESTIMABLE` indicates unavailable official data or insufficient information, not a negative biological conclusion."]
    (root/"AAN_v4_report.md").write_text("\n".join(lines)+"\n")


if __name__ == "__main__": main()
