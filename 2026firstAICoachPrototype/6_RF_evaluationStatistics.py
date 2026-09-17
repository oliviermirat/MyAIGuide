"""
Recompute Figures 2, 4 and 5 from the manuscript and derive the diagnostic statistics
requested by a peer reviewer: sensitivity, specificity, PPV, NPV, false-positive rate,
false-negative rate, and the number of ground-truth days in each category (flare vs not).

This script does NOT re-run the hyperparameter grid search. It reuses the top-15 ranked
hyperparameter sets already saved in results/baseline/hyperparametersGridSearchResults/
summaryResults.xlsx (exactly as pipeline.testing2_ensemble.run_testing2_for_pain does for
the published figures) and retrains only the small ensemble of models needed for inference.
Random forests use a fixed random_state (see libraries/trainRandomForest.py), so results
are deterministic and reproduce the published figures given the same data/code.

Scope (deliberately narrowed): only the paper's own ground-truth "flare" definition
(Scenario A below) is reported, and the ensemble size is fixed at 15 models, matching the
"top 15 models" wording in the Methods/Results text.

Figure -> data mapping (see README pipeline stages and pipeline/testing2_ensemble.py):
  Figure 2 (face/knee/arm, "new dataset" test set only, days 0-163):
      2_baseline.py's data/config: dataMay2023andLater_2026firstAIPrototype_truncated.pkl,
      75/70 split, zero-filled pain days forward-filled, hyperparameters from results/baseline.
  Figure 4 (knee & arm, "new dataset" test set through the "follow-up dataset"):
      4_runInferenceOnExtendedTestSet.py's data/config: dataMay2023andLater_2026firstAIPrototype.pkl
      (unscaled / "NoScaling" run), 55.3/70 split, test set truncated to 2026-06-25,
      hyperparameters from results/baseline.
  Figure 5 (face, same extended test set, before/after the ergonomic intervention):
      5a = same extended test set as Figure 4, "manicTimeRealTime" (time on computer) unscaled
           from 2025-11-01 onward (multiplier = 1.0, i.e. actually recorded values).
      5b = same extended test set, "manicTimeRealTime" multiplied by 0.7 from 2025-11-01 onward
           (the attenuation coefficient reported in the paper).

Ground-truth "flare" definition (Scenario A -- see Methods, "Evaluation metric at the body
region ML model level", and libraries/evaluateRandomForest.py::_prepare_categorized_data):
  High pain = pain > 95th percentile of that figure's own test-set pain distribution.
  Low-pain-clean = pain <= 90th percentile AND the max pain over the preceding 5 days is also
  <= 90th percentile. Days in between (an "intermediate buffer") are EXCLUDED from the binary
  comparison, exactly as in the paper.

Warning/prediction definitions (the traffic light has 3 levels; two natural binary cuts):
  Red-only        - Red counts as a positive warning (Orange and Green = no warning).
  Red-or-Orange   - Red or Orange counts as a positive warning (Green = no warning).

Two ways of counting a "flare" ground-truth day are reported, in two separate workbooks:
  - publication_summary_correlations.xlsx: every day with pain > 95th percentile counts as its
    own ground-truth-positive evaluation instance (this is literally what the paper's own
    evaluation metric does).
  - publication_summary_correlations_onlyFirstFlareDay.xlsx: only the FIRST day of each flare
    episode counts as a ground-truth-positive evaluation instance; the following days of the
    same episode (which are very likely to also sit above the 95th percentile, since pain
    typically stays elevated for a few days and the subject is likely reducing activity in
    response) are excluded from the confusion matrix entirely -- same treatment as the existing
    "buffer" days. See FIRST_FLARE_DAY_MERGE_GAP_DAYS below for how "same episode" is defined.

Outputs (all under results/RF_evaluationStatistics/):
  - publication_summary_correlations.xlsx / publication_summary_correlations_onlyFirstFlareDay.xlsx:
    rows = one statistic each, columns = one (Figure, Pain region, Warning definition)
    combination each, plus a ReadMe sheet.
  - publication_summary_correlations_figure5ProbabilityComparison.xlsx: mean daily predicted
    flare probability for face pain after the ergonomic intervention, WITHOUT vs WITH the
    attenuation coefficient (Figure 5a vs 5b), plus a paired t-test and Wilcoxon signed-rank test.
  - figure2/, figure4_noScaling/, figure5a_unscaled/, figure5b_scaled0.7/: the official
    trafficLights_<pain>.png/.pdf republished by the unmodified plotting code (for a direct
    visual comparison against the published manuscript figures).
  - groundTruthCheck_<figure>_<pain>.png: pain trace colored by the traffic light, with the
    ground-truth flare / low-clean / buffer days marked, to visually confirm the
    confusion-matrix counts below (uses the "every flare day counts" definition).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

from libraries.dataLoader import load_and_preprocess_data
from libraries.run_context import RunPaths, create_run_paths
import pipeline.testing2_ensemble as testing2_ensemble
from pipeline.testing2_ensemble import _test_set_classify_day, run_testing2_for_pain

SCRIPT_ROOT = Path(__file__).resolve().parent

# --- Data sources (must match the scripts that produced the published figures) ---

BASELINE_RUN_NAME = "baseline"  # source of the top-15 hyperparameter sets (results/baseline/...)
N_ENSEMBLE_MODELS = 15  # matches the "top 15 models" wording in Methods/Results

NEW_FILE_PATH = "dataMay2023andLater_2026firstAIPrototype_truncated.pkl"  # 2_baseline.py FILE_PATH
NEW_SPLIT_TRAINVAL_TEST = 0.75
NEW_SPLIT_TRAIN_VAL = 0.7

EXTENDED_FILE_PATH = "dataMay2023andLater_2026firstAIPrototype.pkl"  # 4_runInferenceOnExtendedTestSet.py
EXTENDED_SPLIT_TRAINVAL_TEST = 0.553
EXTENDED_SPLIT_TRAIN_VAL = 0.7
EXTENDED_TEST_END_DATE = "2026-06-25"

FACE_SCALING_COLUMN = "manicTimeRealTime"
FACE_SCALING_CUTOFF_DATE = "2025-11-01"
FACE_ATTENUATION_MULTIPLIER = 0.7

STRESSOR_VARS_MINMAX_SCALER = 0
PAIN_REMOVE_OUTLIERS = 0
TRAINING_DATASET_BEFORE_TESTING = "train_val"

OUT_ROOT = SCRIPT_ROOT / "results" / "RF_evaluationStatistics"

WARNING_DEFS = ("Red only", "Red or Orange")

# Two flare-labeled days are treated as belonging to the SAME flare episode (for the
# "only first flare day" workbook) if they are separated by at most this many non-flare days.
# This is a chained/transitive merge: day C merges with day B if it is within this many days of
# B, even if B itself was merged with an earlier day A -- so a slow-drifting run of flare days
# with small gaps (observed empirically to be up to about a week in this dataset) still collapses
# into one episode, with only its first day counted as a ground-truth-positive evaluation
# instance. Adjust this constant and re-run if a different gap tolerance is wanted.
FIRST_FLARE_DAY_MERGE_GAP_DAYS = 7


def replace_zeros_with_previous(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Verbatim copy of the helper in 2_baseline.py, applied to dfTest before Figure 2 inference."""
    df_clean = df.copy()
    col_idx = df_clean.columns.get_loc(column_name)
    for i in range(1, len(df_clean)):
        if df_clean.iloc[i, col_idx] == 0:
            df_clean.iloc[i, col_idx] = df_clean.iloc[i - 1, col_idx]
    return df_clean


def load_new_dataset_test():
    dfTrainAndVal, dfTrain, _dfVal, dfTest = load_and_preprocess_data(
        NEW_FILE_PATH,
        NEW_SPLIT_TRAINVAL_TEST,
        STRESSOR_VARS_MINMAX_SCALER,
        PAIN_REMOVE_OUTLIERS,
        NEW_SPLIT_TRAIN_VAL,
    )
    for col in ("kneePain", "armPain", "facePain"):
        dfTest = replace_zeros_with_previous(dfTest, col)
    return dfTrainAndVal, dfTrain, dfTest


def load_extended_dataset_test(scale_face_multiplier: float | None = None):
    dfTrainAndVal, dfTrain, _dfVal, dfTest = load_and_preprocess_data(
        EXTENDED_FILE_PATH,
        EXTENDED_SPLIT_TRAINVAL_TEST,
        STRESSOR_VARS_MINMAX_SCALER,
        PAIN_REMOVE_OUTLIERS,
        EXTENDED_SPLIT_TRAIN_VAL,
    )
    dfTest = dfTest[:EXTENDED_TEST_END_DATE]
    if scale_face_multiplier is not None:
        dfTest = dfTest.copy()
        cutoff = pd.Timestamp(FACE_SCALING_CUTOFF_DATE)
        mask = pd.to_datetime(dfTest.index) > cutoff
        dfTest.loc[mask, FACE_SCALING_COLUMN] = (
            dfTest.loc[mask, FACE_SCALING_COLUMN] * scale_face_multiplier
        )
    return dfTrainAndVal, dfTrain, dfTest


def make_run_paths(output_subdir: str) -> RunPaths:
    """Read hyperparameters from results/baseline/, write regenerated figures elsewhere
    (so the originally published PDFs under results/baseline/ are never overwritten)."""
    baseline_paths = create_run_paths(BASELINE_RUN_NAME)
    output_paths = create_run_paths(str(Path("RF_evaluationStatistics") / output_subdir))
    return RunPaths(
        base_dir=output_paths.base_dir,
        output_dir=baseline_paths.output_dir,
        figures_dir=output_paths.figures_dir,
    )


def run_region(pain_type: str, dfTrainAndVal, dfTrain, dfTest, run_paths: RunPaths) -> dict:
    pct_red, pct_yellow, arrays = run_testing2_for_pain(
        pain_type=pain_type,
        save_graph_dont_plot=True,
        save_risk_by_category_dont_plot=True,
        dfTrainAndVal=dfTrainAndVal,
        dfTrain=dfTrain,
        dfTest=dfTest,
        trainingDatasetJustBeforeTesting=TRAINING_DATASET_BEFORE_TESTING,
        run_paths=run_paths,
        return_daily_arrays=True,
    )
    print(f"  -> reproduced pct_above_red={pct_red:.2f}%  pct_orange_only={pct_yellow:.2f}%")
    return arrays


# --- Ground truth labeling (mirrors libraries/evaluateRandomForest.py::_prepare_categorized_data) ---


def ground_truth_labels(actual_pain: np.ndarray) -> np.ndarray:
    """
    Scenario A only (the paper's own evaluation-metric definition): returns an array of
    dtype object with values 'flare', 'not_flare', or 'buffer', one entry per day.
    """
    pain = pd.Series(actual_pain)
    thresh_high = pain.quantile(0.95)
    thresh_low = pain.quantile(0.90)
    is_high = pain > thresh_high
    past_pain_max = pain.rolling(window=5, min_periods=1).max().shift(1)
    is_low_pain = pain <= thresh_low
    is_low_clean = is_low_pain & (past_pain_max <= thresh_low)
    labels = np.where(is_high, "flare", np.where(is_low_clean, "not_flare", "buffer"))
    return np.asarray(labels, dtype=object)


def first_flare_day_only_labels(
    gt_labels: np.ndarray, merge_gap_days: int = FIRST_FLARE_DAY_MERGE_GAP_DAYS
) -> np.ndarray:
    """
    Starting from ground_truth_labels()'s per-day 'flare'/'not_flare'/'buffer' array, keep only
    the FIRST day of each flare episode as 'flare'; every later flare-labeled day belonging to
    the same episode is demoted to 'buffer' (excluded from the confusion matrix, same as the
    original buffer days). Two flare days are considered part of the same episode if they are
    separated by at most `merge_gap_days` non-flare days (chained: see FIRST_FLARE_DAY_MERGE_GAP_DAYS
    above). 'not_flare' and 'buffer' days are left untouched.
    """
    labels = gt_labels.copy()
    flare_idx = np.flatnonzero(labels == "flare")
    if len(flare_idx) == 0:
        return labels
    prev_flare_idx = flare_idx[0]
    for idx in flare_idx[1:]:
        if idx - prev_flare_idx <= merge_gap_days + 1:
            labels[idx] = "buffer"
        prev_flare_idx = idx
    return labels


def warning_flags(traffic_light: list[str], warning_def: str) -> np.ndarray:
    tl = np.asarray(traffic_light, dtype=object)
    if warning_def == "Red only":
        return tl == "red"
    if warning_def == "Red or Orange":
        return np.isin(tl, ["red", "orange"])
    raise ValueError(f"Unknown warning definition: {warning_def}")


STAT_ROWS: list[tuple[str, str]] = [
    ("N_total_days", "N total test-set days"),
    ("N_excluded_buffer_days", "N excluded (buffer) days"),
    ("N_used_days", "N days used (total - buffer)"),
    ("N_groundTruth_flare", "N ground truth = flare"),
    ("N_groundTruth_notFlare", "N ground truth = not flare"),
    ("TP", "True Positives"),
    ("FP", "False Positives"),
    ("TN", "True Negatives"),
    ("FN", "False Negatives"),
    ("Sensitivity_TPR", "Sensitivity (TPR)"),
    ("Specificity_TNR", "Specificity (TNR)"),
    ("PPV_precision", "PPV (Precision)"),
    ("NPV", "NPV"),
    ("FalsePositiveRate", "False Positive Rate"),
    ("FalseNegativeRate", "False Negative Rate"),
    ("Accuracy", "Accuracy"),
]
_ROUND3 = {
    "Sensitivity_TPR",
    "Specificity_TNR",
    "PPV_precision",
    "NPV",
    "FalsePositiveRate",
    "FalseNegativeRate",
    "Accuracy",
}


def confusion_stats(gt_labels: np.ndarray, warned: np.ndarray) -> dict:
    used = gt_labels != "buffer"
    n_total = len(gt_labels)
    n_excluded = int(np.sum(~used))
    gt_pos = (gt_labels == "flare") & used
    gt_neg = (gt_labels == "not_flare") & used

    n_pos = int(np.sum(gt_pos))
    n_neg = int(np.sum(gt_neg))

    tp = int(np.sum(gt_pos & warned))
    fn = int(np.sum(gt_pos & ~warned))
    fp = int(np.sum(gt_neg & warned))
    tn = int(np.sum(gt_neg & ~warned))

    def safe_div(a: int, b: int) -> float:
        return float(a) / b if b > 0 else float("nan")

    stats = {
        "N_total_days": n_total,
        "N_excluded_buffer_days": n_excluded,
        "N_used_days": n_total - n_excluded,
        "N_groundTruth_flare": n_pos,
        "N_groundTruth_notFlare": n_neg,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "Sensitivity_TPR": safe_div(tp, tp + fn),
        "Specificity_TNR": safe_div(tn, tn + fp),
        "PPV_precision": safe_div(tp, tp + fp),
        "NPV": safe_div(tn, tn + fn),
        "FalsePositiveRate": safe_div(fp, fp + tn),
        "FalseNegativeRate": safe_div(fn, fn + tp),
        "Accuracy": safe_div(tp + tn, tp + tn + fp + fn),
    }
    for key in _ROUND3:
        if not np.isnan(stats[key]):
            stats[key] = round(stats[key], 3)
    return stats


# --- Figure 5: mean post-intervention flare probability, with vs without attenuation ---


def compare_post_intervention_probabilities(
    arrays_unscaled: dict, arrays_scaled: dict, cutoff_date: str
) -> dict:
    """
    Paired comparison, over the days strictly after `cutoff_date`, of the ensemble's daily
    predicted flare probability for face pain: WITHOUT the attenuation coefficient (arrays_unscaled,
    i.e. Figure 5a's actually-recorded 'time spent on computer' input) vs WITH it (arrays_scaled,
    i.e. Figure 5b's 0.7-multiplied input). Same calendar days, same trained models, only the
    'manicTimeRealTime' input feature after the cutoff differs -- so this is a paired design, and
    both a paired t-test and a Wilcoxon signed-rank test (parametric / non-parametric) are reported.
    """
    dates_a = pd.to_datetime(arrays_unscaled["dates"])
    dates_b = pd.to_datetime(arrays_scaled["dates"])
    if len(dates_a) != len(dates_b) or (dates_a != dates_b).any():
        raise ValueError("Figure 5a and 5b day indices do not match; cannot pair them.")

    cutoff = pd.Timestamp(cutoff_date)
    mask = dates_a > cutoff

    probs_without = np.asarray(arrays_unscaled["risk_probs"], dtype=float)[mask]
    probs_with = np.asarray(arrays_scaled["risk_probs"], dtype=float)[mask]
    n = int(mask.sum())

    t_stat, t_p = scipy_stats.ttest_rel(probs_without, probs_with)
    try:
        w_stat, w_p = scipy_stats.wilcoxon(probs_without, probs_with)
    except ValueError:
        # all paired differences are zero, or n too small
        w_stat, w_p = float("nan"), float("nan")

    return {
        "N post-intervention days": n,
        "First post-intervention day": str(dates_a[mask].min().date()) if n else "n/a",
        "Last post-intervention day": str(dates_a[mask].max().date()) if n else "n/a",
        "Mean flare probability WITHOUT attenuation": round(float(np.mean(probs_without)), 4),
        "SD flare probability WITHOUT attenuation": round(float(np.std(probs_without, ddof=1)), 4),
        "Mean flare probability WITH attenuation": round(float(np.mean(probs_with)), 4),
        "SD flare probability WITH attenuation": round(float(np.std(probs_with, ddof=1)), 4),
        "Mean paired difference (WITHOUT minus WITH)": round(
            float(np.mean(probs_without - probs_with)), 4
        ),
        "Paired t-test statistic": round(float(t_stat), 4),
        "Paired t-test p-value": float(t_p),
        "Wilcoxon signed-rank statistic": (
            round(float(w_stat), 4) if not np.isnan(w_stat) else float("nan")
        ),
        "Wilcoxon signed-rank p-value": float(w_p),
    }


# --- Visual ground-truth check ---

_TL_COLOR = {"red": "#D55E00", "orange": "#E69F00", "green": "#009E73"}
_GT_BG_COLOR = {"flare": "#FADBD8", "not_flare": "#D5F5E3", "buffer": "#EAECEE"}


def save_ground_truth_check_plot(
    figure_label: str, pain_type_display: str, arrays: dict, out_dir: Path
) -> None:
    actual_pain = np.asarray(arrays["actual_pain"], dtype=float)
    traffic_light = arrays["traffic_light"]
    gt_labels = ground_truth_labels(actual_pain)
    x = np.arange(len(actual_pain))

    fig, ax = plt.subplots(figsize=(16, 5))

    prev_label = None
    start = 0
    for i in range(len(x) + 1):
        cur_label = gt_labels[i] if i < len(x) else None
        if cur_label != prev_label:
            if prev_label is not None:
                ax.axvspan(start - 0.5, i - 0.5, color=_GT_BG_COLOR[prev_label], alpha=0.6, zorder=0)
            start = i
            prev_label = cur_label

    for i in range(len(x) - 1):
        c = _TL_COLOR[traffic_light[i + 1]]
        ax.plot([i, i + 1], [actual_pain[i], actual_pain[i + 1]], color=c, linewidth=1.5, zorder=2)

    ax.set_title(
        f"{figure_label} - {pain_type_display}: pain colored by traffic light,\n"
        "background = ground truth (pink=flare, green=low-pain-clean, grey=buffer)"
    )
    ax.set_xlabel("Test-set day index")
    ax.set_ylabel("Raw pain score (0-10 scale)")
    ax.set_xlim(0, len(x) - 1 if len(x) > 1 else 1)

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    legend_elems = [
        Line2D([0], [0], color=_TL_COLOR["red"], lw=2, label="Traffic light: Red"),
        Line2D([0], [0], color=_TL_COLOR["orange"], lw=2, label="Traffic light: Orange"),
        Line2D([0], [0], color=_TL_COLOR["green"], lw=2, label="Traffic light: Green"),
        Patch(facecolor=_GT_BG_COLOR["flare"], label="Ground truth: flare"),
        Patch(facecolor=_GT_BG_COLOR["not_flare"], label="Ground truth: low-pain clean"),
        Patch(facecolor=_GT_BG_COLOR["buffer"], label="Ground truth: buffer (excluded)"),
    ]
    ax.legend(handles=legend_elems, loc="upper left", fontsize=7, ncol=2)
    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    safe_region = pain_type_display.lower().replace(" ", "_")
    safe_figure = (
        figure_label.lower()
        .replace(" (", "_")
        .replace(")", "")
        .replace(" ", "_")
    )
    out_path = out_dir / f"groundTruthCheck_{safe_figure}_{safe_region}.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> saved {out_path}")


# --- Main ---


def main() -> None:
    import os

    os.chdir(SCRIPT_ROOT)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    testing2_ensemble.N_ENSEMBLE_MODELS_FOR_TEST_PROBS = N_ENSEMBLE_MODELS

    # columns[(figure_label, pain_region, warning_def)] = stats dict
    columns: dict[tuple[str, str, str], dict] = {}
    # same keys, but ground truth uses only the first day of each flare episode as a positive
    columns_first_only: dict[tuple[str, str, str], dict] = {}

    def process_region(figure_label: str, region_display: str, arrays: dict, out_dir: Path) -> None:
        gt_labels = ground_truth_labels(arrays["actual_pain"])
        gt_labels_first_only = first_flare_day_only_labels(gt_labels)
        for warning_def in WARNING_DEFS:
            warned = warning_flags(arrays["traffic_light"], warning_def)
            columns[(figure_label, region_display, warning_def)] = confusion_stats(gt_labels, warned)
            columns_first_only[(figure_label, region_display, warning_def)] = confusion_stats(
                gt_labels_first_only, warned
            )
        save_ground_truth_check_plot(figure_label, region_display, arrays, out_dir)
        plt.close("all")

    # ---------------- Figure 2: new dataset test set, face/knee/arm ----------------
    print("\n=== Figure 2 (new dataset test set) ===")
    dfTrainAndVal_new, dfTrain_new, dfTest_new = load_new_dataset_test()
    run_paths_fig2 = make_run_paths("figure2")
    for pain_type, display in (
        ("kneePain", "Knee"),
        ("facePain", "Face"),
        ("armPain", "Arm"),
    ):
        print(f"- {display} ...")
        arrays = run_region(pain_type, dfTrainAndVal_new, dfTrain_new, dfTest_new, run_paths_fig2)
        process_region("Figure 2", display, arrays, run_paths_fig2.figures_dir)

    # ---------------- Figure 4: extended test set (+ follow-up), knee & arm ----------------
    print("\n=== Figure 4 (new dataset test set + follow-up dataset, unscaled) ===")
    dfTrainAndVal_ext, dfTrain_ext, dfTest_ext_unscaled = load_extended_dataset_test(
        scale_face_multiplier=None
    )
    run_paths_fig4 = make_run_paths("figure4_noScaling")
    for pain_type, display in (("kneePain", "Knee"), ("armPain", "Arm")):
        print(f"- {display} ...")
        arrays = run_region(
            pain_type, dfTrainAndVal_ext, dfTrain_ext, dfTest_ext_unscaled, run_paths_fig4
        )
        process_region("Figure 4", display, arrays, run_paths_fig4.figures_dir)

    # ---------------- Figure 5: extended test set, face, unscaled vs 0.7-attenuated ----------------
    print("\n=== Figure 5a (face, extended test set, unadjusted / actually recorded values) ===")
    run_paths_fig5a = make_run_paths("figure5a_unscaled")
    arrays_5a = run_region(
        "facePain", dfTrainAndVal_ext, dfTrain_ext, dfTest_ext_unscaled, run_paths_fig5a
    )
    process_region("Figure 5a (unadjusted)", "Face", arrays_5a, run_paths_fig5a.figures_dir)

    print("\n=== Figure 5b (face, extended test set, 0.7 attenuation coefficient) ===")
    _dfTrainAndVal_ext2, _dfTrain_ext2, dfTest_ext_scaled07 = load_extended_dataset_test(
        scale_face_multiplier=FACE_ATTENUATION_MULTIPLIER
    )
    run_paths_fig5b = make_run_paths("figure5b_scaled0.7")
    arrays_5b = run_region(
        "facePain", dfTrainAndVal_ext, dfTrain_ext, dfTest_ext_scaled07, run_paths_fig5b
    )
    process_region("Figure 5b (0.7 attenuation)", "Face", arrays_5b, run_paths_fig5b.figures_dir)

    # ---------------- Figure 5: post-intervention flare-probability comparison ----------------
    print("\n=== Comparing post-intervention flare probability: with vs without attenuation ===")
    probability_comparison = compare_post_intervention_probabilities(
        arrays_5a, arrays_5b, FACE_SCALING_CUTOFF_DATE
    )
    for key, val in probability_comparison.items():
        print(f"  {key}: {val}")

    # ---------------- Build the pivoted statistics table ----------------
    # Rows = one statistic each; columns = one (Figure, Pain region, Warning definition) each.
    column_order = [
        ("Figure 2", "Knee", "Red only"),
        ("Figure 2", "Knee", "Red or Orange"),
        ("Figure 2", "Face", "Red only"),
        ("Figure 2", "Face", "Red or Orange"),
        ("Figure 2", "Arm", "Red only"),
        ("Figure 2", "Arm", "Red or Orange"),
        ("Figure 4", "Knee", "Red only"),
        ("Figure 4", "Knee", "Red or Orange"),
        ("Figure 4", "Arm", "Red only"),
        ("Figure 4", "Arm", "Red or Orange"),
        ("Figure 5a (unadjusted)", "Face", "Red only"),
        ("Figure 5a (unadjusted)", "Face", "Red or Orange"),
        ("Figure 5b (0.7 attenuation)", "Face", "Red only"),
        ("Figure 5b (0.7 attenuation)", "Face", "Red or Orange"),
    ]
    col_index = pd.MultiIndex.from_tuples(
        column_order, names=["Figure", "Pain region", "Warning definition"]
    )
    row_keys = [key for key, _display in STAT_ROWS]
    row_display = [display for _key, display in STAT_ROWS]

    def build_stats_df(columns_dict: dict) -> pd.DataFrame:
        data = {col: [columns_dict[col][key] for key in row_keys] for col in column_order}
        df = pd.DataFrame(data, index=row_display)
        df.columns = col_index
        return df

    stats_df = build_stats_df(columns)
    stats_df_first_only = build_stats_df(columns_first_only)

    base_readme_rows = [
        ["Figure 2", "New dataset test set only (days 0-163)."],
        ["Figure 4", "Knee & arm, new dataset test set extended through the follow-up dataset."],
        ["Figure 5a", "Face, extended test set, actual/unadjusted 'time spent on computer'."],
        [
            "Figure 5b",
            f"Face, extended test set, 'time spent on computer' x{FACE_ATTENUATION_MULTIPLIER} "
            f"from {FACE_SCALING_CUTOFF_DATE} onward.",
        ],
        ["Ground truth definition", "Flare = pain > 95th percentile; not-flare = pain <= 90th "
         "percentile AND max pain over the preceding 5 days also <= 90th percentile; days in "
         "between are excluded as a 'buffer'."],
        ["Warning definition: Red only", "Red = positive; Orange and Green = negative."],
        ["Warning definition: Red or Orange", "Red or Orange = positive; only Green = negative."],
    ]

    main_readme_rows = base_readme_rows + [
        ["This workbook's flare-counting rule", "EVERY day with pain > 95th percentile counts "
         "as its own ground-truth-positive instance. See "
         "publication_summary_correlations_onlyFirstFlareDay.xlsx for the alternative."],
    ]
    first_only_readme_rows = base_readme_rows + [
        ["This workbook's flare-counting rule", "Only the FIRST day of each flare episode "
         "counts as a ground-truth-positive instance; later days of the same episode are "
         "excluded (same treatment as buffer days), since they are very likely to also sit "
         "above threshold purely because pain stays elevated for a few days after onset."],
        ["Flare-episode grouping rule", f"Flare-labeled days separated by at most "
         f"{FIRST_FLARE_DAY_MERGE_GAP_DAYS} non-flare days are merged into one episode "
         "(chained). Only each episode's first day is kept as 'flare'. See "
         "first_flare_day_only_labels() / FIRST_FLARE_DAY_MERGE_GAP_DAYS in this script."],
        ["Effect on the statistics", "Only TP, FN, N_groundTruth_flare, N_excluded_buffer_days "
         "and N_used_days differ from publication_summary_correlations.xlsx. "
         "N_groundTruth_notFlare, TN and FP are identical between the two workbooks."],
    ]

    def write_workbook(filename: str, df: pd.DataFrame, readme_rows: list) -> None:
        readme_df = pd.DataFrame(readme_rows, columns=["Item", "Description"])
        xlsx_path = OUT_ROOT / filename
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Statistics", index=True)
            readme_df.to_excel(writer, sheet_name="ReadMe", index=False)
            writer.book.active = 0
            writer.book["Statistics"].sheet_view.tabSelected = True
        print(f"Wrote {xlsx_path}")

    write_workbook("publication_summary_correlations.xlsx", stats_df, main_readme_rows)
    write_workbook(
        "publication_summary_correlations_onlyFirstFlareDay.xlsx",
        stats_df_first_only,
        first_only_readme_rows,
    )

    # ---------------- Write the post-intervention probability comparison workbook ----------------
    prob_readme_rows = [
        ["What is being compared", "Face pain's daily predicted flare probability, days after "
         f"the ergonomic-intervention cutoff ({FACE_SCALING_CUTOFF_DATE}), Figure 5a (WITHOUT "
         "attenuation) vs Figure 5b (WITH attenuation) -- same trained models, same calendar "
         "days, only the input feature after the cutoff differs."],
        ["Why a paired test", "Same days, not independent samples: a paired t-test and a "
         "Wilcoxon signed-rank test are both reported."],
        ["Interpretation", "A positive mean paired difference (WITHOUT minus WITH) means lower "
         "predicted flare risk after the intervention when attenuation is applied."],
    ]
    prob_df = pd.DataFrame(
        list(probability_comparison.items()), columns=["Statistic", "Value"]
    )
    prob_xlsx_path = OUT_ROOT / "publication_summary_correlations_figure5ProbabilityComparison.xlsx"
    with pd.ExcelWriter(prob_xlsx_path, engine="openpyxl") as writer:
        prob_df.to_excel(writer, sheet_name="Statistics", index=False)
        pd.DataFrame(prob_readme_rows, columns=["Item", "Description"]).to_excel(
            writer, sheet_name="ReadMe", index=False
        )
        writer.book.active = 0
        writer.book["Statistics"].sheet_view.tabSelected = True
    print(f"Wrote {prob_xlsx_path}")

    print(f"\nRegenerated figures and ground-truth check plots under {OUT_ROOT}")


if __name__ == "__main__":
    sys.exit(main() or 0)
