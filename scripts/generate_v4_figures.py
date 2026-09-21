#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def table(path): return pd.read_csv(path) if path.exists() else pd.DataFrame()
def main():
    root=Path("results/v4/frozen"); out=root/"figures"; out.mkdir(parents=True,exist_ok=True)
    validation=table(root/"measurement_validation.csv")
    fig,ax=plt.subplots(figsize=(6,4));
    if not validation.empty: validation.groupby("n_cycles").relative_error.median().plot(ax=ax,marker="o")
    ax.set(xlabel="Gait cycles",ylabel="Median relative CV error",title="v4 measurement-rescue convergence"); fig.tight_layout(); fig.savefig(out/"figure_2_measurement_rescue.png",dpi=220); plt.close(fig)
    evidence=table(root/"evidence_matrix.csv")
    fig,ax=plt.subplots(figsize=(7,4));
    if not evidence.empty: evidence.classification.value_counts().plot.bar(ax=ax,color="#1b9e77")
    ax.set(title="v4 context-of-use evidence",ylabel="Candidates"); fig.tight_layout(); fig.savefig(out/"figure_5_context_of_use.png",dpi=220); plt.close(fig)


if __name__ == "__main__": main()
