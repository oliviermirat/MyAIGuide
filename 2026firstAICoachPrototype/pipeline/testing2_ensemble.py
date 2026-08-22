from libraries.featureEngineeringFunctions import featureEngineering
from libraries.evaluateRandomForest import plot_risk_by_pain_category, get_roc_auc
from libraries.trainRandomForest import randomForestTrain
from libraries.dataLoader import load_and_preprocess_data
from libraries.run_context import RunPaths, SUMMARY_RESULTS_XLSX, create_run_paths
from pipeline.gridConfigs import get_candidate_config
from sklearn.preprocessing import MinMaxScaler
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import sys
import os
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# Default column headers for percent_above_thresholds_traffic_light.xlsx when PAIN_TYPES are
# (knee, face, arm) in that order (including old_dataset foreheadEyes / fingerHandArm).
TRAFFIC_LIGHT_PAIN_REGION_COLUMNS: Tuple[str, str, str] = ("Knee", "Face", "Arm")

# Random forest P(warning) on traffic-light figures: subdued so colored pain stays primary.
TRAFFIC_LIGHT_PROB_COLOR = "#A8D8F0"
TRAFFIC_LIGHT_PROB_ALPHA = 0.5

SHOW_PLOT_MINMAX = False
SHOW_PLOT_MAXPAIN_CLIP_STANDARDSCALER = False
SILENT_MODE = 0
TEST_ON_TEST_DATASET = True

# If True, replace `risk_probs` with an aggregation over the last 5 days
# (including the current day). Used by the traffic-light rolling-threshold rule
# and the risk plots. Mean vs max is controlled by the second boolean below.
USE_ROLLING_LAST_5_DAYS_FOR_RISK_PROBS = False
ROLLING_LAST_5_DAYS_USE_MAX = True  # if False => rolling mean

# Number of top rows from hyperparametersGridSearchResults/summaryResults.xlsx to ensemble
# (average test-set warning probabilities across these models).
N_ENSEMBLE_MODELS_FOR_TEST_PROBS = 15
# Written under bestHyperparametersSetResults/ after each pain type in run_testing2_for_pain.
ENSEMBLE_TEST_ROC_AUC_XLSX = "ensemble_test_roc_auc.xlsx"
# Used to resolve the CANDIDATES column in summaryResults.xlsx (must match the grid search run).
SUMMARY_RESULTS_CANDIDATES_DATA_VERSION = "new"
# If your summary file came from a script that used a custom candidate config (e.g. combined
# stressors), set this to that same dict; otherwise leave as None.
ENSEMBLE_CANDIDATES_CONFIG: Optional[dict] = None


def _params_from_summary_results_row(
    row: pd.Series, pain_type: str, candidates_config: dict
) -> dict:
    """Build the params dict for training from a row of summaryResults.xlsx."""
    return {
        "ACUTE_WINDOW": int(row["ACUTE_WINDOW"]),
        "CHRONIC_WINDOW": int(row["CHRONIC_WINDOW"]),
        "ONLY_USE_ACWR": False,
        "INCLUDE_NB_PREVIOUS_DAY_PAIN": 0,
        "SEEK_MOST_IMPORTANT_FEATURES": True,
        "NB_TOP_FEATURES_TO_KEEP": int(row["NB_TOP_FEATURES_TO_KEEP"]),
        "HIGH_PAIN_QUARTILE_DEFINITION": float(row["HIGH_PAIN_QUARTILE_DEFINITION"]),
        "WARNING_WINDOW": 1,
        "CANDIDATES": candidates_config[pain_type][row["CANDIDATES"]],
    }


def _traffic_light_figtitle(pain_type: str) -> str:
    if pain_type == "armPain" or pain_type == "fingerHandArmPain":
        return "Arm Pain Colored by Risk Prediction"
    if pain_type == "kneePain":
        return "Knee Pain Colored by Risk Prediction"
    return "Face Pain Colored by Risk Prediction"


def _rolling_mean_or_max_last_n_days(
    x: np.ndarray, n_days: int, *, use_max: bool
) -> np.ndarray:
    """
    For each index i, aggregate x over [max(0, i-n_days+1), i] (inclusive).
    If `use_max` is True => rolling max, else rolling mean.
    """
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return x
    if n_days < 1:
        raise ValueError("n_days must be >= 1")
    out = np.empty_like(x, dtype=float)
    for i in range(len(x)):
        start = max(0, i - n_days + 1)
        window = x[start : i + 1]
        out[i] = float(np.max(window) if use_max else np.mean(window))
    return out


def _test_set_thresholds_for_day(
    risk_probs: np.ndarray,
    actual_pain: np.ndarray,
    day_index: int,
    realPainValueYellow: float = 3.0,
    realPainValueRed: float = 3.3,
) -> tuple:
    """
    For test-set day ``day_index`` (0-based), using only prior days 0..day_index-1:

    If there is at least one prior day with pain in
    [``realPainValueYellow``, ``realPainValueRed``) and at least one with pain below
    ``realPainValueYellow``:
    minProb = min predicted probability over days with pain below ``realPainValueYellow``;
    maxProbYellow = max predicted probability over days with pain in
    [``realPainValueYellow``, ``realPainValueRed``);
    if maxProbYellow - minProb > 0.05: yellow = maxProbYellow - (maxProbYellow - minProb) / 10,
    red = maxProbYellow.

    Otherwise: let mu, sigma be mean and sample std (ddof=1) of predicted probabilities
    over 0..day_index-1 (sigma = 0 if only one prior day);
    yellow = mu + 2 * sigma, red = mu + 3 * sigma.
    """
    if day_index < 2:
        return float("nan"), float("nan")
    hist_p = risk_probs[:day_index]
    hist_a = actual_pain[:day_index]
    high = (hist_a >= realPainValueYellow) & (hist_a < realPainValueRed)
    low = hist_a < realPainValueYellow
    if np.any(high) and np.any(low):
        minProb = float(np.min(hist_p[low]))
        maxProbYellow = float(np.max(hist_p[high]))
        if maxProbYellow - minProb > 0.05:
            span = maxProbYellow - minProb
            yellow_thresh = maxProbYellow - span / 10.0
            red_thresh = maxProbYellow
            return yellow_thresh, red_thresh

    mu = float(np.mean(hist_p))
    sigma = float(np.std(hist_p, ddof=1)) if len(hist_p) > 1 else 0.0
    yellow_thresh = mu + 0.5 * sigma
    red_thresh = mu + 1.0 * sigma
    return yellow_thresh, red_thresh


def _test_set_classify_day(
    risk_probs: np.ndarray,
    actual_pain: np.ndarray,
    day_index: int,
    realPainValueYellow: float = 3.0,
    realPainValueRed: float = 3.3,
) -> str:
    """
    Risk zone for test day ``day_index`` (0-based) using the same rolling thresholds as
    ``_test_set_thresholds_for_day``. Days 0 and 1 are always green (no rolling rule).
    Returns 'red' | 'orange' | 'green'.
    """
    if day_index < 2:
        return "green"
    prob = risk_probs[day_index]
    yellow_thresh, red_thresh = _test_set_thresholds_for_day(
        risk_probs,
        actual_pain,
        day_index,
        realPainValueYellow=realPainValueYellow,
        realPainValueRed=realPainValueRed,
    )
    if prob >= red_thresh:
        return "red"
    if prob >= yellow_thresh:
        return "orange"
    return "green"


def _test_set_traffic_color_for_segment(
    i: int,
    risk_probs: np.ndarray,
    actual_pain: np.ndarray,
    realPainValueYellow: float = 3.0,
    realPainValueRed: float = 3.3,
) -> str:
    """
    Color for segment [i, i+1] using the risk at day index i+1. The first segment (i==0),
    covering the first two test days, is always green. For i>=1, uses the same rule as
    ``_test_set_classify_day`` for day i+1.
    Returns 'red' | 'orange' | 'green' for the quick plot.
    """
    if i == 0:
        return "green"
    return _test_set_classify_day(
        risk_probs,
        actual_pain,
        i + 1,
        realPainValueYellow=realPainValueYellow,
        realPainValueRed=realPainValueRed,
    )


def save_traffic_light_percent_excel(
    run_paths: RunPaths,
    column_names: Sequence[str],
    pct_above_red: Sequence[float],
    pct_yellow_only: Sequence[float],
) -> None:
    """
    Write traffic-light summary percents (test set, rolling-threshold rule) to
    bestHyperparametersSetResults/percent_above_thresholds_traffic_light.xlsx: two rows x len(column_names) columns.
    """
    names = list(column_names)
    reds = list(pct_above_red)
    yellows = list(pct_yellow_only)
    if not (len(names) == len(reds) == len(yellows)):
        raise ValueError("column_names, pct_above_red, pct_yellow_only must have the same length")
    run_paths.figures_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_paths.figures_dir / "percent_above_thresholds_traffic_light.xlsx"
    df = pd.DataFrame(
        [reds, yellows],
        index=[
            "Percent above red thresh",
            "Percent yellow (medium risk only)",
        ],
        columns=names,
    )
    df.to_excel(out_path, index=True)
    print(f"Saved traffic-light percent summary to {out_path.resolve()}")


def _find_optimal_threshold_percentages_and_save(
    risk_probs: np.ndarray,
    actual_pain: np.ndarray,
    sorted_probs_val: np.ndarray,
) -> float:
    """
    Find the smallest max_red_alerts_percent and max_yellow_alerts_percent such
    that the prediction on the day with the highest actual pain for this body
    region is in the red zone (i.e. red_thresh <= that prediction).
    Then recompute percent above red/yellow with those thresholds.

    Returns:
        Percent above red thresh (0-100) on the test set with the optimal threshold
        (same quantity stored per combination as min_red_pct_* in summaryResults.xlsx).
    """
    if len(risk_probs) == 0 or len(sorted_probs_val) == 0 or len(actual_pain) == 0:
        return float("nan")
    if len(risk_probs) != len(actual_pain):
        return float("nan")
    idx_max_pain = np.argmax(actual_pain)
    prediction_on_max_pain_day = risk_probs[idx_max_pain]
    n_val = len(sorted_probs_val)

    # Smallest red/yellow percents such that threshold <= prediction_on_max_pain_day
    k_red = np.searchsorted(sorted_probs_val, prediction_on_max_pain_day, side="right") - 1
    k_red = max(0, k_red)
    min_red_percent = 1.0 - (k_red / n_val)

    red_thresh_opt = sorted_probs_val[int(n_val * (1 - min_red_percent))]
    pct_above_red_opt = (np.sum(risk_probs >= red_thresh_opt) / len(risk_probs)) * 100

    return pct_above_red_opt


def run_testing2_single_combination_for_pain(
    pain_type: str,
    params: dict,
    df_train_and_val,
    df_val,
    df_test,
    run_paths: RunPaths,
) -> Tuple[float, float, float]:
    """
    Train a model with the given params on train_and_val, compute validation and test
    predictions, and return
    (min_red_pct, test_roc_auc, test_p_val_roc) where min_red_pct is from
    _find_optimal_threshold_percentages_and_save (percent above red with optimal threshold;
    same quantity as min_red_pct_* in summaryResults.xlsx), and test_roc_auc /
    test_p_val_roc come from get_roc_auc on the test-set predictions (same metric as
    validation custom_score / p_val_corr_coeff).
    """
    acute_window = int(params["ACUTE_WINDOW"])
    chronic_window = int(params["CHRONIC_WINDOW"])
    candidates = params["CANDIDATES"]
    only_use_acwr = bool(params["ONLY_USE_ACWR"])
    include_nb_previous_day_pain = int(params["INCLUDE_NB_PREVIOUS_DAY_PAIN"])

    model, _, top_features = randomForestTrain(
        df_train_and_val,
        pain_type,
        params,
        SILENT_MODE,
        TEST_ON_TEST_DATASET,
        figures_dir=run_paths.figures_dir,
    )

    df_val_fe, _ = featureEngineering(
        df_val.copy(),
        candidates,
        only_use_acwr,
        acute_window,
        chronic_window,
        include_nb_previous_day_pain,
        pain_type,
    )
    X_val = df_val_fe[top_features].copy()
    results_val = df_val_fe[[pain_type]].copy()
    results_val.loc[:, "predictedProbsWarning"] = model.predict_proba(X_val)[:, 1]
    results_val = results_val.iloc[chronic_window:]
    sorted_probs_val = np.sort(results_val["predictedProbsWarning"].values)

    df_test_fe, _ = featureEngineering(
        df_test.copy(),
        candidates,
        only_use_acwr,
        acute_window,
        chronic_window,
        include_nb_previous_day_pain,
        pain_type,
    )
    X_test = df_test_fe[top_features].copy()
    results_test = df_test_fe[[pain_type]].copy()
    results_test.loc[:, "predictedProbsWarning"] = model.predict_proba(X_test)[:, 1]
    results_test = results_test.iloc[chronic_window:]
    risk_probs = results_test["predictedProbsWarning"].values
    if USE_ROLLING_LAST_5_DAYS_FOR_RISK_PROBS:
        risk_probs = _rolling_mean_or_max_last_n_days(
            risk_probs, 5, use_max=ROLLING_LAST_5_DAYS_USE_MAX
        )
    actual_pain = results_test[pain_type].values

    metrics_test = get_roc_auc(results_test, pain_type)
    test_roc_auc = metrics_test["custom_score"]
    test_p_val = metrics_test["p_val_corr_coeff"]
    if test_roc_auc == -10000:
        test_roc_auc = float("nan")
    if test_p_val == -10000:
        test_p_val = float("nan")

    min_red_pct = _find_optimal_threshold_percentages_and_save(
        risk_probs,
        actual_pain,
        sorted_probs_val,
    )
    return min_red_pct, test_roc_auc, test_p_val


def save_test_set_scores_to_figures(
    df_train_and_val,
    df_test,
    run_paths: RunPaths,
    pain_types: list,
) -> None:
    """
    For the best combination (from best_params_<pain>.json), train on train+val,
    evaluate on test set to get custom_score (Cohen's d) per pain type, then compute
    mean_custom_score and adjusted_score and save them to bestHyperparametersSetResults/test_set_scores.xlsx.
    """
    run_paths.figures_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_paths.figures_dir / "test_set_scores.xlsx"

    scores = {}
    for pain_type in pain_types:
        json_filename = run_paths.output_dir / f"best_params_{pain_type}.json"
        if not json_filename.exists():
            print(f"Warning: {json_filename} not found; skipping test-set scores for {pain_type}.")
            continue
        try:
            with json_filename.open("r") as f:
                params = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read {json_filename}: {e}")
            continue
        chronic_window = int(params["CHRONIC_WINDOW"])
        candidates = params["CANDIDATES"]
        only_use_acwr = bool(params["ONLY_USE_ACWR"])
        include_nb_previous_day_pain = int(params.get("INCLUDE_NB_PREVIOUS_DAY_PAIN", 0))

        try:
            model, _, top_features = randomForestTrain(
                df_train_and_val,
                pain_type,
                params,
                SILENT_MODE,
                TEST_ON_TEST_DATASET,
                figures_dir=run_paths.figures_dir,
            )
            df_test_fe, _ = featureEngineering(
                df_test.copy(),
                candidates,
                only_use_acwr,
                int(params["ACUTE_WINDOW"]),
                chronic_window,
                include_nb_previous_day_pain,
                pain_type,
            )
            X_test = df_test_fe[top_features].copy()
            results_test = df_test_fe[[pain_type]].copy()
            results_test.loc[:, "predictedProbsWarning"] = model.predict_proba(X_test)[:, 1]
            results_test = results_test.iloc[chronic_window:]
            metrics = get_roc_auc(results_test, pain_type)
            scores[pain_type] = metrics["custom_score"]
        except Exception as e:
            print(f"Warning: error computing test-set score for {pain_type}: {e}")
            continue

    if not scores:
        df_placeholder = pd.DataFrame({
            "metric": ["note"],
            "value": ["Could not compute: no best_params_<pain>.json found in output_dir, or all attempts failed."],
        })
        df_placeholder.to_excel(out_path, index=False)
        print(f"Wrote placeholder to {out_path.resolve()} (no scores computed)")
        return

    score_values = list(scores.values())
    mean_custom_score = float(np.mean(score_values))
    adjusted_score = mean_custom_score - float(np.std(score_values))

    rows = [{"metric": pt, "value": scores[pt]} for pt in pain_types if pt in scores]
    rows.append({"metric": "mean_custom_score", "value": mean_custom_score})
    rows.append({"metric": "adjusted_score", "value": adjusted_score})
    df = pd.DataFrame(rows)
    df.to_excel(out_path, index=False)
    print(f"Saved test-set mean_custom_score and adjusted_score to {out_path.resolve()}")


def _pain_type_to_ensemble_region(pain_type: str) -> str:
    if pain_type == "kneePain":
        return "knee"
    if pain_type in ("facePain", "foreheadEyesPain"):
        return "face"
    if pain_type in ("armPain", "fingerHandArmPain"):
        return "arm"
    raise ValueError(f"Unknown pain_type for ensemble ROC-AUC file: {pain_type}")


def _update_ensemble_test_roc_auc_file(
    run_paths: RunPaths, pain_type: str, test_roc_auc: float
) -> None:
    """Merge one body-region test ROC-AUC (top-N ensemble) into ensemble_test_roc_auc.xlsx."""
    run_paths.figures_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_paths.figures_dir / ENSEMBLE_TEST_ROC_AUC_XLSX
    region = _pain_type_to_ensemble_region(pain_type)
    if out_path.is_file():
        df = pd.read_excel(out_path)
    else:
        df = pd.DataFrame(columns=["region", "test_roc_auc"])
    df = df.loc[df["region"] != region]
    df = pd.concat(
        [df, pd.DataFrame([{"region": region, "test_roc_auc": test_roc_auc}])],
        ignore_index=True,
    )
    df.to_excel(out_path, index=False)


def load_ensemble_test_roc_auc_metrics(figures_dir: Path) -> dict[str, float]:
    """
    Test-set ROC-AUC from the top-N ensemble (see N_ENSEMBLE_MODELS_FOR_TEST_PROBS).
    Expects ensemble_test_roc_auc.xlsx written by run_testing2_for_pain for each pain type.
    """
    path = figures_dir / ENSEMBLE_TEST_ROC_AUC_XLSX
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Re-run the testing2 ensemble step (2_*.py) for this experiment."
        )
    df = pd.read_excel(path)
    if "region" not in df.columns or "test_roc_auc" not in df.columns:
        raise ValueError(f"{path}: expected columns 'region' and 'test_roc_auc'")
    by_region = {
        str(row["region"]): float(row["test_roc_auc"])
        for _, row in df.iterrows()
        if pd.notna(row["test_roc_auc"])
    }
    for key in ("face", "knee", "arm"):
        if key not in by_region:
            raise ValueError(f"{path}: missing region '{key}'")
    face = by_region["face"]
    knee = by_region["knee"]
    arm = by_region["arm"]
    return {
        "face_auc": face,
        "knee_auc": knee,
        "arm_auc": arm,
        "mean_auc": float(np.mean([face, knee, arm])),
    }


def run_testing2_for_pain(
    pain_type: str,
    save_graph_dont_plot: bool,
    save_risk_by_category_dont_plot: bool,
    dfTrainAndVal,
    dfTrain,
    dfTest,
    trainingDatasetJustBeforeTesting: str,
    run_paths: RunPaths,
    candidates_config: Optional[dict] = None,
) -> Tuple[float, float]:
    """
    Extended evaluation script with additional publication-ready plots.
    Returns (percent_above_red, percent_yellow_only) on the test set using the rolling
    traffic-light rule (same quantities aggregated into percent_above_thresholds_traffic_light.xlsx).
    """
    figtitle = _traffic_light_figtitle(pain_type)

    summary_path = run_paths.output_dir / SUMMARY_RESULTS_XLSX
    if not summary_path.exists():
        print(f"ERROR: Could not find {summary_path}. Run training/grid search first.")
        sys.exit(1)

    summary_df = pd.read_excel(summary_path)
    n_take = min(N_ENSEMBLE_MODELS_FOR_TEST_PROBS, len(summary_df))
    if n_take < 1:
        print(f"ERROR: {summary_path} has no rows.")
        sys.exit(1)
    if n_take < N_ENSEMBLE_MODELS_FOR_TEST_PROBS:
        print(
            f"Warning: summaryResults has only {len(summary_df)} row(s); "
            f"using {n_take} model(s) for the ensemble."
        )

    if candidates_config is None:
        candidates_config = ENSEMBLE_CANDIDATES_CONFIG or get_candidate_config(
            SUMMARY_RESULTS_CANDIDATES_DATA_VERSION
        )
    ensemble_rows = summary_df.head(n_take)
    param_list = [
        _params_from_summary_results_row(row, pain_type, candidates_config)
        for _, row in ensemble_rows.iterrows()
    ]
    cw_max = max(int(p["CHRONIC_WINDOW"]) for p in param_list)

    df_train_for_ensemble = (
        dfTrainAndVal if trainingDatasetJustBeforeTesting == "train_val" else dfTrain
    )

    pred_rows: List[np.ndarray] = []
    for params in param_list:
        model, _, top_features = randomForestTrain(
            df_train_for_ensemble,
            pain_type,
            params,
            SILENT_MODE,
            TEST_ON_TEST_DATASET,
            figures_dir=run_paths.figures_dir,
        )
        df_test_fe, _ = featureEngineering(
            dfTest.copy(),
            params["CANDIDATES"],
            bool(params["ONLY_USE_ACWR"]),
            int(params["ACUTE_WINDOW"]),
            int(params["CHRONIC_WINDOW"]),
            int(params["INCLUDE_NB_PREVIOUS_DAY_PAIN"]),
            pain_type,
        )
        X_test = df_test_fe[top_features].copy()
        pred_rows.append(model.predict_proba(X_test)[:, 1])

    prob_matrix = np.vstack(pred_rows)
    avg_probs = np.mean(prob_matrix, axis=0)

    print("")
    print("Pain type:", pain_type)

    # Launching analysis on 'test set' (ensemble mean of top-N summaryResults models)
    results = pd.DataFrame(
        {pain_type: dfTest[pain_type].values},
        index=dfTest.index,
    )
    results.loc[:, "predictedProbsWarning"] = avg_probs
    results = results.iloc[cw_max:]

    plot_risk_by_pain_category(
        results,
        pain_type,
        save_risk_by_category_dont_plot,
        output_dir=run_paths.output_dir,
        figures_dir=run_paths.figures_dir,
    )

    scaler = MinMaxScaler()
    cols_to_plot = [pain_type, "predictedProbsWarning"]
    scaled_values = scaler.fit_transform(results[cols_to_plot])
    scaled_values[:, 1] = results["predictedProbsWarning"]

    plt.figure(figsize=(20, 8))
    plt.plot(scaled_values)
    if save_graph_dont_plot:
        raw_preds_path = run_paths.figures_dir / f"rawPreds_{pain_type}.png"
        plt.savefig(raw_preds_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    # Generate Traffic Light Signals (test set: rolling thresholds; see helpers above)
    pain_scaled = scaled_values[:, 0]
    risk_probs = results["predictedProbsWarning"].values
    if USE_ROLLING_LAST_5_DAYS_FOR_RISK_PROBS:
        risk_probs = _rolling_mean_or_max_last_n_days(
            risk_probs, 5, use_max=ROLLING_LAST_5_DAYS_USE_MAX
        )
    actual_pain = results[pain_type].values
    n_test = len(risk_probs)

    n_red = 0
    n_yellow_only = 0
    for d in range(n_test):
        zone = _test_set_classify_day(risk_probs, actual_pain, d)
        if zone == "red":
            n_red += 1
        elif zone == "orange":
            n_yellow_only += 1

    pct_above_red = (n_red / n_test) * 100 if n_test else 0.0
    pct_yellow_only = (n_yellow_only / n_test) * 100 if n_test else 0.0
    print("Percent above red thresh:", pct_above_red)
    print("Percent yellow (medium risk only):", pct_yellow_only)

    # Quick visualization plot
    fig, ax1 = plt.subplots(figsize=(20, 8))
    x_days = np.arange(len(risk_probs))
    ax2 = ax1.twinx()
    ax2.plot(
        x_days,
        risk_probs,
        color=TRAFFIC_LIGHT_PROB_COLOR,
        alpha=TRAFFIC_LIGHT_PROB_ALPHA,
        linewidth=1.5,
        zorder=1,
    )
    ax2.set_ylabel("Prediction probability")
    ax2.set_ylim(0.0, 1.0)
    ax1.set_zorder(ax2.get_zorder() + 1)
    ax1.patch.set_visible(False)

    for i in range(len(pain_scaled) - 1):
        c = _test_set_traffic_color_for_segment(i, risk_probs, actual_pain)
        ax1.plot(
            [i, i + 1],
            [pain_scaled[i], pain_scaled[i + 1]],
            color=c,
            linewidth=2,
            zorder=2,
        )
    ax1.set_title(figtitle)
    ax1.set_ylabel("Scaled Pain Intensity")
    ax1.set_xlabel("Days")

    custom_lines = [
        Line2D([0], [0], color="green", lw=2, label="Low Risk"),
        Line2D([0], [0], color="orange", lw=2, label="Medium Risk"),
        Line2D([0], [0], color="red", lw=2, label="High Risk"),
        Line2D(
            [0],
            [0],
            color=TRAFFIC_LIGHT_PROB_COLOR,
            lw=1.5,
            alpha=TRAFFIC_LIGHT_PROB_ALPHA,
            label="Prediction probability",
        ),
    ]
    ax1.legend(handles=custom_lines, loc="upper left")
    if save_graph_dont_plot:
        traffic_png = run_paths.figures_dir / f"trafficLights_{pain_type}.png"
        fig.savefig(traffic_png, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    # Publication-ready plot
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 7,
            "axes.titlesize": 7,
            "axes.labelsize": 7,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "axes.linewidth": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    width_in = 183 / 25.4
    height_in = width_in * 0.4
    fig, ax = plt.subplots(figsize=(width_in, height_in))

    COLOR_HIGH_RISK = "#D55E00"
    COLOR_MED_RISK = "#E69F00"
    COLOR_LOW_RISK = "#009E73"
    _zone_to_pub = {
        "red": COLOR_HIGH_RISK,
        "orange": COLOR_MED_RISK,
        "green": COLOR_LOW_RISK,
    }

    x_days_pub = np.arange(len(risk_probs))
    ax2 = ax.twinx()
    ax2.plot(
        x_days_pub,
        risk_probs,
        color=TRAFFIC_LIGHT_PROB_COLOR,
        alpha=TRAFFIC_LIGHT_PROB_ALPHA,
        linewidth=0.9,
        zorder=1,
    )
    ax2.set_ylabel("Prediction probability")
    ax2.set_ylim(0.0, 1.0)
    ax2.tick_params(axis="y", labelsize=6)
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)

    for i in range(len(pain_scaled) - 1):
        zone = _test_set_traffic_color_for_segment(i, risk_probs, actual_pain)
        c = _zone_to_pub[zone]
        ax.plot(
            [i, i + 1],
            [pain_scaled[i], pain_scaled[i + 1]],
            color=c,
            linewidth=1.0,
            zorder=2,
        )

    ax.set_title(figtitle)
    ax.set_ylabel("Scaled Pain Intensity")
    ax.set_xlabel("Days")

    custom_lines = [
        Line2D([0], [0], color=COLOR_LOW_RISK, lw=1.0, label="Low Risk"),
        Line2D([0], [0], color=COLOR_MED_RISK, lw=1.0, label="Medium Risk"),
        Line2D([0], [0], color=COLOR_HIGH_RISK, lw=1.0, label="High Risk"),
        Line2D(
            [0],
            [0],
            color=TRAFFIC_LIGHT_PROB_COLOR,
            lw=0.9,
            alpha=TRAFFIC_LIGHT_PROB_ALPHA,
            label="Prediction probability",
        ),
    ]

    ax.legend(handles=custom_lines, loc="upper left", frameon=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    plt.tight_layout()

    if save_graph_dont_plot:
        save_path = run_paths.figures_dir / f"trafficLights_{pain_type}.pdf"
        plt.savefig(save_path, format="pdf", bbox_inches="tight")
    else:
        plt.show()

    evaluationMetrics = get_roc_auc(results, pain_type)
    print("Evaluation metrics:", evaluationMetrics)
    ens_roc = float(evaluationMetrics["custom_score"])
    if ens_roc == -10000:
        ens_roc = float("nan")
    _update_ensemble_test_roc_auc_file(run_paths, pain_type, ens_roc)

    return pct_above_red, pct_yellow_only


def _cli_main() -> None:
    """
    Entry point for running testing2.py directly from the console.
    """
    pain_type = sys.argv[1]
    save_graph_dont_plot = bool(int(sys.argv[2])) if len(sys.argv) >= 3 else False
    save_risk_by_category_dont_plot = bool(int(sys.argv[3])) if len(sys.argv) >= 4 else False

    file_path = sys.argv[4]
    stressorVarsMinMaxScaler = int(sys.argv[5])
    painRemoveOutliers = int(sys.argv[6])
    split_percent_trainval_test = float(sys.argv[7])
    split_percent_train_val = float(sys.argv[8])
    _ = sys.argv[9]  # legacy CLI position (was testingDataset)
    trainingDatasetJustBeforeTesting = sys.argv[10]

    # Optional run name as last argument to route results/<run>/ subfolders
    run_name = sys.argv[11] if len(sys.argv) > 11 else None

    dfTrainAndVal, dfTrain, dfVal, dfTest = load_and_preprocess_data(
        file_path,
        split_percent_trainval_test,
        stressorVarsMinMaxScaler,
        painRemoveOutliers,
        split_percent_train_val,
    )

    run_paths = create_run_paths(run_name)

    pr, py = run_testing2_for_pain(
        pain_type=pain_type,
        save_graph_dont_plot=save_graph_dont_plot,
        save_risk_by_category_dont_plot=save_risk_by_category_dont_plot,
        dfTrainAndVal=dfTrainAndVal,
        dfTrain=dfTrain,
        dfTest=dfTest,
        trainingDatasetJustBeforeTesting=trainingDatasetJustBeforeTesting,
        run_paths=run_paths,
    )
    save_traffic_light_percent_excel(run_paths, [pain_type], [pr], [py])


if __name__ == "__main__":
    _cli_main()
