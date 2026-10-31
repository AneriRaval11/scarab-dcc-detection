"""Reproduce the GMM-vs-reference-flag result for one gridded SAPHIR orbit.

    python scripts/reproduce_gmm_result.py data/sap_dict.pkl

Writes results/tables/gmm_vs_flag.csv and results/figures/gmm_vs_dcc_flag_confusion_matrices.png
"""
import pickle
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.mixture import GaussianMixture

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import grid_func  # noqa: E402

warnings.filterwarnings("ignore")
NOVAL = -9999.0
FEATURES = ["stznsp", "bt1sp", "bt2sp", "bt3sp", "bt4sp", "bt5sp", "mask"]
BANDS = {"Near-nadir (incidence angle < 26 deg)": (0, 26), "Off-nadir (incidence angle >= 26 deg)": (26, 90)}


def evaluate(d, flag, features, lo, hi, seed=0):
    sel = (d["stznsp"] != NOVAL) & (d["bt2sp"] != NOVAL) & (d["stznsp"] >= lo) & (d["stznsp"] < hi)
    X = np.column_stack([d[f][sel] for f in features])
    y = flag[sel]
    pred = GaussianMixture(2, covariance_type="full", random_state=seed).fit_predict(X)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    if cm[0, 0] + cm[1, 1] < cm[0, 1] + cm[1, 0]:   # GMM cluster ids are arbitrary: pick the matching orientation
        cm = cm[:, ::-1]
    return int(sel.sum()), int((y == 1).sum()), cm


def main(pkl_path):
    d = pickle.load(open(pkl_path, "rb"))
    flag, _ = grid_func.dcc_flag(*[d[k] for k in ["bt1sp", "bt2sp", "bt3sp", "bt4sp", "bt5sp", "stznsp"]])
    rows, mats = [], {}
    for name, feats in {"all features": FEATURES, "without TB1": [f for f in FEATURES if f != "bt1sp"]}.items():
        for band, (lo, hi) in BANDS.items():
            n, pos, cm = evaluate(d, flag, feats, lo, hi)
            pct = cm / cm.sum(axis=1, keepdims=True) * 100
            rows.append(dict(features=name, band=band, n_pixels=n, n_dcc=pos, dcc_share_pct=100 * pos / n,
                             dcc_recall_pct=pct[1, 1], false_alarm_pct=pct[0, 1]))
            if name == "all features":
                mats[band] = (n, pos, pct)
    out = pd.DataFrame(rows)
    (ROOT / "results" / "tables").mkdir(parents=True, exist_ok=True)
    out.round(2).to_csv(ROOT / "results" / "tables" / "gmm_vs_flag.csv", index=False)
    print(out.round(2).to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.9))
    for ax, (band, (n, pos, pct)) in zip(axes, mats.items()):
        sns.heatmap(pct, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=100, cbar=False,
                    xticklabels=["Non-DCC", "DCC"], yticklabels=["Non-DCC", "DCC"], ax=ax, annot_kws={"size": 13})
        ax.set_title(f"{band}\nn = {n:,} pixels, of which DCC = {pos:,}", fontsize=10.5)
        ax.set_xlabel("GMM prediction (unsupervised)")
        ax.set_ylabel("Reference DCC flag")
    fig.suptitle("Gaussian Mixture clustering vs SAPHIR-derived DCC flag, one Megha-Tropiques orbit (1 Jan 2014)\n"
                 "values are % of each reference class", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "figures" / "gmm_vs_dcc_flag_confusion_matrices.png", dpi=170)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "data" / "sap_dict.pkl")
