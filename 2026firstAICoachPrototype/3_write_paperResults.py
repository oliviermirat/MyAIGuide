"""
Build paper outputs from completed pipeline runs:
  - results/combinedAnalysis/figure2.png and figure2.pdf — two rows × one column per experiment:
    mean_custom_score (validation) vs mean_test_roc_auc (test); row 0 = all grid rows; row 1 =
    HIGH_PAIN_QUARTILE_DEFINITION == 0.8 only; panel titles = experiment folder name (split camelCase) + Pearson r
  - results/combinedAnalysis/table1.xlsx (sheet Table1: reduced metrics row set — no 10th percentile;
    first four rows = test ROC-AUC from the top-N ensemble (ensemble_test_roc_auc.xlsx);
    two Pearson r rows for mean_custom_score: all grid rows vs HIGH_PAIN_QUARTILE_DEFINITION == 0.8 only)

Expects each experiment under results/<run_name>/ with hyperparametersGridSearchResults/summaryResults.xlsx
and bestHyperparametersSetResults/ensemble_test_roc_auc.xlsx from the testing2 ensemble step.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from libraries.run_context import (
    BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR,
    HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR,
    SUMMARY_RESULTS_XLSX,
)
from pipeline.testing2_ensemble import load_ensemble_test_roc_auc_metrics

SCRIPT_ROOT = Path(__file__).resolve().parent
RESULTS_ROOT = SCRIPT_ROOT / "results"
COMBINED_DIR = RESULTS_ROOT / "combinedAnalysis"

# Experiment folder names (under results/)
EXP_BASELINE_NEW = "baseline"
EXP_ALL_STRESSORS = "allStressorsCombined"
# Results folder names (under results/) — must match RUN_NAME in 2_low_resolution / 2_very_low_resolution.
EXP_LOW_RESOLUTION = "lowResolution"
EXP_VERY_LOW_RESOLUTION = "veryLowResolution"
EXP_SLEEP_ONLY = "sleepOnly"
EXP_OLD = "oldDataset"

TABLE1_COLUMNS = [
    "New dataset baseline",
    "New dataset All stressors combined",
    "New dataset Low Resolution body region related stressors only",
    "New dataset Very Low Resolution body region related stressors only",
    "New dataset Sleep only",
    "Old dataset Selected body region related stressors only",
]

# Columns left → right in multi-panel figures (must match TABLE1_COLUMNS order)
EXPERIMENT_FOLDER_ORDER = (
    EXP_BASELINE_NEW,
    EXP_ALL_STRESSORS,
    EXP_LOW_RESOLUTION,
    EXP_VERY_LOW_RESOLUTION,
    EXP_SLEEP_ONLY,
    EXP_OLD,
)
# EXPERIMENT_FOLDER_ORDER = (
    # EXP_BASELINE_NEW,
    # EXP_ALL_STRESSORS,
    # EXP_LOW_RESOLUTION,
    # EXP_VERY_LOW_RESOLUTION,
    # EXP_OLD,
# )

TABLE1_ROWS = [
    "face ROC-AUC score on the test set for the set of hyperparameters selected by the grid search",
    "knee ROC-AUC score on the test set for the set of hyperparameters selected by the grid search",
    "arm ROC-AUC score on the test set for the set of hyperparameters selected by the grid search",
    "mean ROC-AUC for the set of hyperparameters selected by the grid search",
    "maximum mean ROC-AUC that could have been reached for another set of hyperparameters",
    "80th percentile of mean ROC-AUC that could have been reached for another set of hyperparameters",
    "50th percentile of mean ROC-AUC that could have been reached for another set of hyperparameters",
    "Pearson r — mean_custom_score (validation) vs mean_test_roc_auc (test), all grid rows",
    "Pearson r — mean_custom_score (validation) vs mean_test_roc_auc (test), only 0.8 threshold",
]


def _summary_path(exp_folder: str) -> Path:
    return (
        RESULTS_ROOT
        / exp_folder
        / HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR
        / SUMMARY_RESULTS_XLSX
    )


def load_summary(exp_folder: str) -> pd.DataFrame:
    p = _summary_path(exp_folder)
    if not p.is_file():
        raise FileNotFoundError(f"Missing summary results: {p}")
    df = pd.read_excel(p)
    if df.empty:
        raise ValueError(f"Empty summary file: {p}")
    return df


def _filter_high_pain_quartile_08(df: pd.DataFrame, summary_path: Path) -> pd.DataFrame:
    """Subset summary rows to HIGH_PAIN_QUARTILE_DEFINITION == 0.8 (figure2 row 1 and table1 Pearson r)."""
    if "HIGH_PAIN_QUARTILE_DEFINITION" not in df.columns:
        raise ValueError(f"{summary_path}: missing column HIGH_PAIN_QUARTILE_DEFINITION")
    hp = df["HIGH_PAIN_QUARTILE_DEFINITION"].to_numpy(dtype=float)
    out = df.loc[np.isclose(hp, 0.8)].copy()
    if out.empty:
        raise ValueError(f"{summary_path}: no rows with HIGH_PAIN_QUARTILE_DEFINITION == 0.8")
    return out


def _square_axis_limits_pooled(x: np.ndarray, y: np.ndarray, pad_frac: float = 0.02) -> tuple[float, float]:
    """
    Single [lo, hi] for both x and y so each panel uses the same min/max on both axes.
    Pooled min/max across all x and y values; optional padding so points are not flush to edges.
    """
    if x.size == 0 or y.size == 0:
        return 0.0, 1.0
    lo = float(min(np.nanmin(x), np.nanmin(y)))
    hi = float(max(np.nanmax(x), np.nanmax(y)))
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return 0.0, 1.0
    span = hi - lo
    if span <= 1e-15:
        pad = 0.01 * (abs(lo) if abs(lo) > 1e-12 else 1.0)
        return lo - pad, hi + pad
    pad = pad_frac * span
    return lo - pad, hi + pad


def _experiment_folder_display_name(folder: str) -> str:
    """e.g. baseline -> Baseline; camelCase folders split before caps; spaced names unchanged."""
    s = folder
    prev = None
    while s != prev:
        prev = s
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    return " ".join(w.capitalize() for w in s.split())


def _fmt_pearson_r_title(r: float) -> str:
    """Two decimals for subplot title; NA if undefined."""
    if r is None or (isinstance(r, float) and np.isnan(r)):
        return "NA"
    return f"{float(r):.2f}"


def _figure2_panel_title(name: str, r_display: str) -> str:
    """Plain experiment name + mathtext with bold ``r = …`` (matches Table 1 correlation)."""
    if r_display == "NA":
        math_r = r"\mathbf{r = \mathrm{NA}}"
    else:
        math_r = rf"\mathbf{{r = {r_display}}}"
    return f"{name} (${math_r}$)"


def save_figure2(
    data_by_exp: dict[str, pd.DataFrame],
    data_by_exp_q08: dict[str, pd.DataFrame],
    out_dir: Path,
) -> None:
    """
    Two rows × N columns: both rows are mean_custom_score (validation) vs mean_test_roc_auc (test).
    Row 0: all grid rows.
    Row 1: HIGH_PAIN_QUARTILE_DEFINITION == 0.8 only.
    Each panel title: experiment folder name via _experiment_folder_display_name + Pearson r (two decimals)
    for mean_custom_score vs mean_test_roc_auc on that panel's data.
    """
    _f5c_title_fs = 15
    _f5c_label_fs = 14
    _f5c_tick_fs = 7
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 7,
            "axes.titlesize": _f5c_title_fs,
            "axes.labelsize": _f5c_label_fs,
            "xtick.labelsize": _f5c_tick_fs,
            "ytick.labelsize": _f5c_tick_fs,
            "axes.linewidth": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    
    EXPERIMENT_FOLDER_ORDER_2 = (
        EXP_BASELINE_NEW,
        EXP_ALL_STRESSORS,
        EXP_LOW_RESOLUTION,
        EXP_VERY_LOW_RESOLUTION,
        EXP_OLD,
    )
    
    nrows = 1
    ncols = len(EXPERIMENT_FOLDER_ORDER_2)
    fig_w = 183 / 25.4 * 2.35 * (ncols / 5)
    fig_h = fig_w * 0.42
    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h))

    color_mc = "#0072B2"

    subs0: list[pd.DataFrame] = []
    subs1: list[pd.DataFrame] = []
    rs0: list[float] = []
    rs1: list[float] = []
    stats0: list[dict[str, float]] = []
    stats1: list[dict[str, float]] = []

    for exp_key in EXPERIMENT_FOLDER_ORDER_2:
        df0 = data_by_exp[exp_key]
        df1 = data_by_exp_q08[exp_key]
        _require_validation_columns(df0, _summary_path(exp_key))
        _require_validation_columns(df1, _summary_path(exp_key))
        sub0 = df0[["mean_custom_score", "mean_test_roc_auc"]].dropna()
        sub1 = df1[["mean_custom_score", "mean_test_roc_auc"]].dropna()
        if sub0.empty:
            raise ValueError(f"No complete rows for Figure 2 (all rows) in {_summary_path(exp_key)}")
        if sub1.empty:
            raise ValueError(f"No complete rows for Figure 2 (0.8 quartile) in {_summary_path(exp_key)}")
        subs0.append(sub0)
        subs1.append(sub1)
        cor0 = validation_vs_test_correlations(df0)
        cor1 = validation_vs_test_correlations(df1)
        rs0.append(cor0["r_mean_custom"])
        rs1.append(cor1["r_mean_custom"])
        stats0.append({"p": cor0["p_mean_custom"], "n": len(sub0)})
        stats1.append({"p": cor1["p_mean_custom"], "n": len(sub1)})

    x0 = np.concatenate([s["mean_custom_score"].to_numpy(dtype=float) for s in subs0])
    y0 = np.concatenate([s["mean_test_roc_auc"].to_numpy(dtype=float) for s in subs0])
    x1 = np.concatenate([s["mean_custom_score"].to_numpy(dtype=float) for s in subs1])
    y1 = np.concatenate([s["mean_test_roc_auc"].to_numpy(dtype=float) for s in subs1])
    lo0, hi0 = _square_axis_limits_pooled(x0, y0)
    lo1, hi1 = _square_axis_limits_pooled(x1, y1)

    print("Figure 2 panels — Pearson r (validation mean_custom_score vs test mean_test_roc_auc):")
    for j, exp_key in enumerate(EXPERIMENT_FOLDER_ORDER_2):
        name = _experiment_folder_display_name(exp_key)
        print(
            f"  {name}: r={rs0[j]:.3f}, p={stats0[j]['p']:.3g}, n={stats0[j]['n']}"
        )

    for j, exp_key in enumerate(EXPERIMENT_FOLDER_ORDER_2):
        name = _experiment_folder_display_name(exp_key)
        r0 = _fmt_pearson_r_title(rs0[j])
        r1 = _fmt_pearson_r_title(rs1[j])
        title0 = _figure2_panel_title(name, r0)
        title1 = _figure2_panel_title(name, r1)

        axes[j].scatter(
            subs0[j]["mean_custom_score"],
            subs0[j]["mean_test_roc_auc"],
            s=10,
            alpha=0.65,
            edgecolors="none",
            c=color_mc,
        )
        axes[j].set_xlabel("validation set ROC-AUC", fontsize=_f5c_label_fs)
        axes[j].set_title(title0, fontsize=_f5c_title_fs, pad=3)
        axes[j].grid(True, alpha=0.3, linewidth=0.5)
        axes[j].set_xlim(lo0, hi0)
        axes[j].set_ylim(lo0, hi0)
        axes[j].set_aspect("equal", adjustable="box")
        
        if False:
          axes[1, j].scatter(
              subs1[j]["mean_custom_score"],
              subs1[j]["mean_test_roc_auc"],
              s=10,
              alpha=0.65,
              edgecolors="none",
              c=color_mc,
          )
          axes[1, j].set_xlabel("validation set ROC-AUC", fontsize=_f5c_label_fs)
          axes[1, j].set_title(title1, fontsize=_f5c_title_fs, pad=3)
          axes[1, j].grid(True, alpha=0.3, linewidth=0.5)
          axes[1, j].set_xlim(lo1, hi1)
          axes[1, j].set_ylim(lo1, hi1)
          axes[1, j].set_aspect("equal", adjustable="box")

    for i in range(nrows):
        axes[i].set_ylabel("test set ROC-AUC", fontsize=_f5c_label_fs)

    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = "figure2"
    png_path = out_dir / f"{stem}.png"
    pdf_path = out_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {png_path} and {pdf_path}")


def _ensemble_test_metrics(exp_folder: str) -> dict:
    """Top-N ensemble test ROC-AUC (see pipeline.testing2_ensemble.N_ENSEMBLE_MODELS_FOR_TEST_PROBS)."""
    figures_dir = (
        RESULTS_ROOT / exp_folder / BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR
    )
    return load_ensemble_test_roc_auc_metrics(figures_dir)


def _require_test_columns(df: pd.DataFrame, path: Path) -> None:
    needed = [
        "test_roc_auc_face",
        "test_p_val_face",
        "test_roc_auc_knee",
        "test_p_val_knee",
        "test_roc_auc_arm",
        "test_p_val_arm",
        "mean_test_roc_auc",
    ]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}. Re-run the corresponding 2_*.py test phase.")


def _require_validation_columns(df: pd.DataFrame, path: Path) -> None:
    needed = ["mean_custom_score", "adjusted_score"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}. Expected from grid-search merge.")


def _pearson_r_p(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Pearson r and two-tailed p-value; drop pairwise NaNs. Need n >= 2 pairs."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 2:
        return float("nan"), float("nan")
    r, p = pearsonr(x[mask], y[mask])
    return float(r), float(p)


def validation_vs_test_correlations(df: pd.DataFrame) -> dict[str, float]:
    """
    Across all hyperparameter rows in summaryResults: correlate validation summaries
    with mean_test_roc_auc (test).
    """
    y = df["mean_test_roc_auc"].values.astype(float)
    mc = df["mean_custom_score"].values.astype(float)
    adj = df["adjusted_score"].values.astype(float)
    r_mc, p_mc = _pearson_r_p(mc, y)
    r_adj, p_adj = _pearson_r_p(adj, y)
    return {
        "r_mean_custom": r_mc,
        "p_mean_custom": p_mc,
        "r_adjusted": r_adj,
        "p_adjusted": p_adj,
    }


def _mean_auc_distribution(df: pd.DataFrame) -> np.ndarray:
    s = df["mean_test_roc_auc"].dropna().astype(float)
    if s.empty:
        return np.array([])
    return s.values


def _grid_stats(df: pd.DataFrame) -> dict:
    v = _mean_auc_distribution(df)
    if len(v) == 0:
        return dict(
            max=np.nan,
            p10=np.nan,
            p20=np.nan,
            p50=np.nan,
            p80=np.nan,
            p90=np.nan,
        )
    return dict(
        max=float(np.nanmax(v)),
        p10=float(np.nanpercentile(v, 10)),
        p20=float(np.nanpercentile(v, 20)),
        p50=float(np.nanpercentile(v, 50)),
        p80=float(np.nanpercentile(v, 80)),
        p90=float(np.nanpercentile(v, 90)),
    )


def build_table1(
    data_by_exp: dict[str, pd.DataFrame],
    data_by_exp_q08: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Metrics without 10th percentile row; rows 0–3 = ensemble test ROC-AUC (top-N models);
    Pearson r for mean_custom_score vs mean_test_roc_auc on all grid rows and on
    HIGH_PAIN_QUARTILE_DEFINITION == 0.8 rows only.
    """
    col_keys = list(EXPERIMENT_FOLDER_ORDER)
    table = pd.DataFrame(index=TABLE1_ROWS, columns=TABLE1_COLUMNS, dtype=object)
    for col_name, exp in zip(TABLE1_COLUMNS, col_keys):        
        df = data_by_exp[exp]
        df_q08 = data_by_exp_q08[exp]
        _require_test_columns(df, _summary_path(exp))
        _require_validation_columns(df, _summary_path(exp))
        _require_validation_columns(df_q08, _summary_path(exp))
        ens = _ensemble_test_metrics(exp)
        gs = _grid_stats(df)
        cor_all = validation_vs_test_correlations(df)
        cor_q08 = validation_vs_test_correlations(df_q08)
        table.loc[TABLE1_ROWS[0], col_name] = ens["face_auc"]
        table.loc[TABLE1_ROWS[1], col_name] = ens["knee_auc"]
        table.loc[TABLE1_ROWS[2], col_name] = ens["arm_auc"]
        table.loc[TABLE1_ROWS[3], col_name] = ens["mean_auc"]
        table.loc[TABLE1_ROWS[4], col_name] = gs["max"]
        table.loc[TABLE1_ROWS[5], col_name] = gs["p80"]
        table.loc[TABLE1_ROWS[6], col_name] = gs["p50"]
        table.loc[TABLE1_ROWS[7], col_name] = cor_all["r_mean_custom"]
        table.loc[TABLE1_ROWS[8], col_name] = cor_q08["r_mean_custom"]
            
    return table


def main() -> None:
    os.chdir(SCRIPT_ROOT)
    COMBINED_DIR.mkdir(parents=True, exist_ok=True)

    baseline_df = load_summary(EXP_BASELINE_NEW)
    old_df = load_summary(EXP_OLD)
    low_resolution_df = load_summary(EXP_LOW_RESOLUTION)
    very_low_resolution_df = load_summary(EXP_VERY_LOW_RESOLUTION)
    alls_df = load_summary(EXP_ALL_STRESSORS)
    sleep_df = load_summary(EXP_SLEEP_ONLY)

    _require_test_columns(baseline_df, _summary_path(EXP_BASELINE_NEW))
    _require_test_columns(old_df, _summary_path(EXP_OLD))
    _require_test_columns(low_resolution_df, _summary_path(EXP_LOW_RESOLUTION))
    _require_test_columns(very_low_resolution_df, _summary_path(EXP_VERY_LOW_RESOLUTION))
    _require_test_columns(alls_df, _summary_path(EXP_ALL_STRESSORS))
    _require_test_columns(sleep_df, _summary_path(EXP_SLEEP_ONLY))

    data_by_exp = {
        EXP_BASELINE_NEW: baseline_df,
        EXP_ALL_STRESSORS: alls_df,
        EXP_LOW_RESOLUTION: low_resolution_df,
        EXP_VERY_LOW_RESOLUTION: very_low_resolution_df,
        EXP_SLEEP_ONLY: sleep_df,
        EXP_OLD: old_df,
    }
    data_by_exp_q08 = {
        exp: _filter_high_pain_quartile_08(data_by_exp[exp], _summary_path(exp))
        for exp in EXPERIMENT_FOLDER_ORDER
    }
    save_figure2(data_by_exp, data_by_exp_q08, COMBINED_DIR)

    table1_df = build_table1(data_by_exp, data_by_exp_q08)
    
    table1_df = table1_df.apply(pd.to_numeric, errors="coerce").round(2)
    table1_path = COMBINED_DIR / "table1.xlsx"
    
    with pd.ExcelWriter(table1_path, engine="openpyxl") as writer:
        table1_df.to_excel(writer, sheet_name="Table1", index=True)
    print(f"Wrote {table1_path} (sheet: Table1; values rounded to 2 decimals)")


if __name__ == "__main__":
    main()
