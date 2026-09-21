#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
def main():
 root=Path('results/v4_2/frozen');out=root/'figures';out.mkdir(exist_ok=True); runs=pd.read_csv(root/'h2_repeated_cv_runs.csv');
 fig,ax=plt.subplots(figsize=(7,3));ax.text(.05,.7,'Raw footfalls → 8 reconstructed inputs → V1 PKMAS equivalence → longitudinal score',fontsize=11);ax.text(.05,.35,'Stopped before scoring: calibrated metric rear-foot coordinates are unavailable.',fontsize=10,color='crimson');ax.axis('off');fig.tight_layout();fig.savefig(out/'figure_1_h4_bridge.png',dpi=220);plt.close(fig)
 a=pd.read_csv(root/'v1_reconstruction_agreement.csv');fig,ax=plt.subplots(figsize=(7,3));ax.text(.05,.6,'Analytical-equivalence gate: NOT ESTIMABLE',fontsize=14);ax.text(.05,.35,a.reason.iloc[0],wrap=True);ax.axis('off');fig.tight_layout();fig.savefig(out/'figure_2_h4_agreement_gate.png',dpi=220);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,3));ax.text(.05,.6,'Long-term stability: NOT ESTIMABLE',fontsize=14);ax.text(.05,.35,'No eight-input score was generated after the failed equivalence gate.',fontsize=10);ax.axis('off');fig.tight_layout();fig.savefig(out/'figure_3_h4_stability.png',dpi=220);plt.close(fig)
 d=runs[runs.level.eq('row')];fig,ax=plt.subplots(figsize=(7,3));[ax.hist(d[col],bins=24,alpha=.45,label=col.replace('delta_','')) for col in ['delta_rmse','delta_mae','delta_spearman_rho']];ax.axvline(0,color='black');ax.legend();ax.set(title='H2-R: repeated participant-grouped CV deltas',xlabel='Extended minus baseline');fig.tight_layout();fig.savefig(out/'figure_4_h2_robustness.png',dpi=220);plt.close(fig)
if __name__=='__main__':main()
