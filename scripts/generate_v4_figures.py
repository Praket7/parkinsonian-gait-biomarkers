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
    primary=table(root/"primary_associations.csv")
    fig,ax=plt.subplots(figsize=(7,4));
    if not primary.empty:
        plot=primary.dropna(subset=["effect"]).sort_values("effect"); ax.barh(plot.feature,plot.effect,color="#377eb8"); ax.axvline(0,color="black",lw=1)
    ax.set(title="v4 phenotype association map",xlabel="Standardized severity association"); fig.tight_layout(); fig.savefig(out/"figure_3_phenotype_map.png",dpi=220); plt.close(fig)
    mobilised=table(root/"mobilised_stability.csv")
    fig,ax=plt.subplots(figsize=(7,4));
    if not mobilised.empty: ax.barh(mobilised.feature,mobilised.median_standardized_effect,color="#984ea3")
    ax.axvline(0,color="black",lw=1); ax.set(title="Mobilise-D half-sample longitudinal stability",xlabel="Median standardized effect"); fig.tight_layout(); fig.savefig(out/"figure_4_external_stability.png",dpi=220); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4));
    if not evidence.empty:
        status=evidence.pivot_table(index="feature",columns="association_status",aggfunc="size",fill_value=0); status.plot(kind="barh",stacked=True,ax=ax)
    ax.set(title="Prospective candidate qualification status",xlabel="Candidates"); fig.tight_layout(); fig.savefig(out/"figure_1_qualification_matrix.png",dpi=220); plt.close(fig)


if __name__ == "__main__": main()
