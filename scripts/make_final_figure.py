"""Redraw the final result figure from the confusion-matrix values printed by
notebooks/01_saphir_preprocessing_dcc_gmm.ipynb (rows = reference class, % of that class).

    python scripts/make_final_figure.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Row-normalised confusion matrices (%), copied from the notebook output.
# rows: reference [non-DCC, DCC]; columns: GMM prediction [non-DCC, DCC]
RESULTS = {
    "Near-nadir pixels\n(incidence angle 0-25 deg, n = 7,857)": np.array([[97.84, 2.16], [0.00, 100.00]]),
    "Off-nadir pixels\n(incidence angle 26-52 deg, n = 11,146)": np.array([[90.24, 9.76], [23.12, 76.88]]),
}
LABELS = ["Non-DCC", "DCC"]

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
for ax, (title, cm) in zip(axes, RESULTS.items()):
    sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=100, cbar=False,
                xticklabels=LABELS, yticklabels=LABELS, ax=ax, annot_kws={"size": 13})
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("GMM prediction (unsupervised)")
    ax.set_ylabel("Reference DCC flag")
fig.suptitle("Gaussian Mixture clustering vs SAPHIR-derived DCC flag, 1 Jan 2014 orbit\n"
             "(values are % of each reference class)", fontsize=12)
fig.tight_layout()
out = Path(__file__).resolve().parents[1] / "results" / "figures" / "gmm_vs_dcc_flag_confusion_matrices.png"
fig.savefig(out, dpi=170)
print("saved", out)
