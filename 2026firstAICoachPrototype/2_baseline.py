import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from pipeline.gridConfigs import CONFIG_GRID_DEBUG, CONFIG_GRID_STANDARD, get_candidate_config
from libraries.dataLoader import load_and_preprocess_data
from libraries.run_context import (
    BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR,
    HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR,
    RunPaths,
    SUMMARY_RESULTS_XLSX,
    create_run_paths,
)
from pipeline.training import run_grid_search_for_pain
from pipeline.plotStressorGroupsComparison import plot_stressor_groups_comparison
from pipeline.plotCompareAllTrainingHyperparameters import (
    plot_compare_all_training_hyperparameters,
)
from pipeline.replaceCandidatesInResultFile import replace_candidates_in_result_file
from pipeline.findBestCombinations import find_best_combination
from pipeline.testing2 import (
    TRAFFIC_LIGHT_PAIN_REGION_COLUMNS,
    run_testing2_single_combination_for_pain,
    run_testing2_for_pain,
    save_test_set_scores_to_figures,
    save_traffic_light_percent_excel,
)


RUN_NAME = "baseline"
DATA_VERSION = "new"
USE_DEBUG_GRID = False
if "RUNALL_MASTER_DEBUG_GRID" in os.environ:
    USE_DEBUG_GRID = os.environ["RUNALL_MASTER_DEBUG_GRID"].strip().lower() in ("1", "true", "yes")
USE_ALL_VARIABLES_CANDIDATE_SET = False

FILE_PATH = "newDataset.pkl"
STRESSOR_VARS_MINMAX_SCALER = 0
PAIN_REMOVE_OUTLIERS = 0
SPLIT_PERCENT_TRAINVAL_TEST = 0.75
SPLIT_PERCENT_TRAIN_VAL = 0.7

TEST_ON_VAL_DATASET = True
TRAINING_DATASET_BEFORE_TESTING = "train_val"

PAIN_TYPES = ["kneePain", "facePain", "armPain"]


def _params_from_row(row: pd.Series, pain_type: str, candidates_config: dict) -> dict:
    """Build the params dict for training/testing from a row of summaryResults.xlsx."""
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


def clean_run_directories(run_base: Path) -> None:
    for sub in (
        HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR,
        BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR,
    ):
        target = run_base / sub
        if target.exists():
            response = input(
                f"WARNING: This will delete ALL files in '{target}'. Continue? (y/n): "
            )
            if response.lower() != "y":
                print(f"Skipping cleanup of {target}.")
                continue

            print(f"Cleaning {target}...")
            for filename in os.listdir(target):
                file_path = target / filename
                try:
                    if file_path.is_file() or file_path.is_symlink():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil

                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            target.mkdir(parents=True, exist_ok=True)
            print(f"Created {target}")


def run_testing_all_combinations(
    ranked_df: pd.DataFrame,
    candidates_config: dict,
    df_train_and_val,
    df_val,
    df_test,
    run_paths: RunPaths,
) -> pd.DataFrame:
    """
    For each row in ranked_df (each hyperparameter set), train on train_val, run on test,
    call _find_optimal_threshold_percentages_and_save, and collect
    the minimum red-day percentage per pain type, test-set ROC-AUC and p-value per pain type
    (same construction as validation score_* / p_val_*), and mean_test_roc_auc. Writes the
    new columns onto ranked_df and returns it.
    """
    n = len(ranked_df)
    min_red_knee = [None] * n
    min_red_face = [None] * n
    min_red_arm = [None] * n
    test_roc_knee = [float("nan")] * n
    test_roc_face = [float("nan")] * n
    test_roc_arm = [float("nan")] * n
    test_p_knee = [float("nan")] * n
    test_p_face = [float("nan")] * n
    test_p_arm = [float("nan")] * n

    for i in range(n):
        row = ranked_df.iloc[i]
        print(f"--- Hyperparameter set {i + 1}/{n} ---")
        for pain_type in PAIN_TYPES:
            params = _params_from_row(row, pain_type, candidates_config)
            try:
                min_red_pct, roc_auc_t, p_val_t = run_testing2_single_combination_for_pain(
                    pain_type=pain_type,
                    params=params,
                    df_train_and_val=df_train_and_val,
                    df_val=df_val,
                    df_test=df_test,
                    run_paths=run_paths,
                )
                if pain_type == "kneePain":
                    min_red_knee[i] = min_red_pct
                    test_roc_knee[i] = roc_auc_t
                    test_p_knee[i] = p_val_t
                elif pain_type == "facePain":
                    min_red_face[i] = min_red_pct
                    test_roc_face[i] = roc_auc_t
                    test_p_face[i] = p_val_t
                else:
                    min_red_arm[i] = min_red_pct
                    test_roc_arm[i] = roc_auc_t
                    test_p_arm[i] = p_val_t
            except Exception as e:
                print(f"  Error for {pain_type}: {e}")
                if pain_type == "kneePain":
                    min_red_knee[i] = float("nan")
                elif pain_type == "facePain":
                    min_red_face[i] = float("nan")
                else:
                    min_red_arm[i] = float("nan")

    ranked_df = ranked_df.copy()
    ranked_df["min_red_pct_knee"] = min_red_knee
    ranked_df["min_red_pct_face"] = min_red_face
    ranked_df["min_red_pct_arm"] = min_red_arm
    ranked_df["test_roc_auc_face"] = test_roc_face
    ranked_df["test_p_val_face"] = test_p_face
    ranked_df["test_roc_auc_knee"] = test_roc_knee
    ranked_df["test_p_val_knee"] = test_p_knee
    ranked_df["test_roc_auc_arm"] = test_roc_arm
    ranked_df["test_p_val_arm"] = test_p_arm
    ranked_df["mean_test_roc_auc"] = ranked_df[
        ["test_roc_auc_face", "test_roc_auc_knee", "test_roc_auc_arm"]
    ].mean(axis=1)
    return ranked_df


def plot_min_red_percentages_by_combination(
    ranked_df: pd.DataFrame,
    run_paths: RunPaths,
) -> None:
    """Create and save a graph: x = combination index 1..N, y = percent of days for each pain type."""
    n = len(ranked_df)
    x = list(range(1, n + 1))

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

    if "min_red_pct_knee" in ranked_df.columns:
        ax.plot(x, ranked_df["min_red_pct_knee"].values, "o-", label="Knee", markersize=4)
    if "min_red_pct_face" in ranked_df.columns:
        ax.plot(x, ranked_df["min_red_pct_face"].values, "s-", label="Face", markersize=4)
    if "min_red_pct_arm" in ranked_df.columns:
        ax.plot(x, ranked_df["min_red_pct_arm"].values, "^-", label="Arm", markersize=4)

    ax.set_xlabel("Hyperparameter set")
    ax.set_ylabel("Percent of days (%)")
    ax.set_title("Percent of days by pain region and hyperparameter set")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    out_png = run_paths.figures_dir / "min_red_pct_all_combinations.png"
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    out_pdf = run_paths.figures_dir / "min_red_pct_all_combinations.pdf"
    plt.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved plot to {out_png} and {out_pdf}")


def main() -> None:
    print("")
    print("Using", "CONFIG_GRID_DEBUG" if USE_DEBUG_GRID else "CONFIG_GRID_STANDARD")

    response = input("Continue? (y/n): ")
    if response.lower() != "y":
        print("Aborting run.")
        return

    run_paths = create_run_paths(RUN_NAME)
    clean_run_directories(run_paths.base_dir)

    candidates_config = get_candidate_config(DATA_VERSION)
    grid_template = CONFIG_GRID_DEBUG if USE_DEBUG_GRID else CONFIG_GRID_STANDARD

    dfTrainAndVal, dfTrain, dfVal, dfTest = load_and_preprocess_data(
        FILE_PATH,
        SPLIT_PERCENT_TRAINVAL_TEST,
        STRESSOR_VARS_MINMAX_SCALER,
        PAIN_REMOVE_OUTLIERS,
        SPLIT_PERCENT_TRAIN_VAL,
    )

    print(f"--- Starting training grid search for {len(PAIN_TYPES)} pain types ---")
    for pain_type in PAIN_TYPES:
        run_grid_search_for_pain(
            pain_type=pain_type,
            grid_template=grid_template,
            candidates_config=candidates_config,
            df_train=dfTrain,
            df_val=dfVal,
            test_on_val_dataset=TEST_ON_VAL_DATASET,
            include_all_candidate_sets=USE_ALL_VARIABLES_CANDIDATE_SET,
            run_paths=run_paths,
        )

    print("--- Custom score summary by candidate set (console) ---")
    for pain_type in PAIN_TYPES:
        plot_stressor_groups_comparison(pain_type, run_paths)

    print("--- Replacing candidate lists with group labels ---")
    for pain_type in PAIN_TYPES:
        replace_candidates_in_result_file(pain_type, candidates_config, run_paths)

    print("--- Combined hyperparameter statistics (console) ---")
    plot_compare_all_training_hyperparameters(
        knee_pain="kneePain",
        face_pain="facePain",
        arm_pain="armPain",
        run_paths=run_paths,
    )

    print("--- Finding best shared hyperparameter combination ---")
    find_best_combination(
        kneePain="kneePain",
        facePain="facePain",
        armPain="armPain",
        candidates_config=candidates_config,
        run_paths=run_paths,
    )

    ranked_path = run_paths.output_dir / SUMMARY_RESULTS_XLSX
    if not ranked_path.exists():
        print(f"ERROR: {ranked_path} not found. Aborting.")
        return

    print("--- Running random forest on test set for ALL hyperparameter combinations ---")
    ranked_df = pd.read_excel(ranked_path)
    ranked_df = run_testing_all_combinations(
        ranked_df=ranked_df,
        candidates_config=candidates_config,
        df_train_and_val=dfTrainAndVal,
        df_val=dfVal,
        df_test=dfTest,
        run_paths=run_paths,
    )
    ranked_df.to_excel(ranked_path, index=False)
    print(
        f"Updated {ranked_path} with min_red_pct_* columns, test_roc_auc_* / test_p_val_* "
        "(test-set ROC-AUC and p-values), and mean_test_roc_auc."
    )

    print("--- Saving test-set mean_custom_score and adjusted_score to figures ---")
    save_test_set_scores_to_figures(
        df_train_and_val=dfTrainAndVal,
        df_test=dfTest,
        run_paths=run_paths,
        pain_types=PAIN_TYPES,
    )

    print("--- Creating min red percentage graph ---")
    plot_min_red_percentages_by_combination(ranked_df, run_paths)

    print("--- Running testing2 on held-out test set (best combination; traffic light plots) ---")
    pct_red_tl = []
    pct_yellow_tl = []
    for pain_type in PAIN_TYPES:
        pr, py = run_testing2_for_pain(
            pain_type=pain_type,
            save_graph_dont_plot=True,
            save_risk_by_category_dont_plot=True,
            dfTrainAndVal=dfTrainAndVal,
            dfTrain=dfTrain,
            dfTest=dfTest,
            trainingDatasetJustBeforeTesting=TRAINING_DATASET_BEFORE_TESTING,
            run_paths=run_paths,
        )
        pct_red_tl.append(pr)
        pct_yellow_tl.append(py)
    save_traffic_light_percent_excel(
        run_paths,
        TRAFFIC_LIGHT_PAIN_REGION_COLUMNS,
        pct_red_tl,
        pct_yellow_tl,
    )

    print("\n--- All requested experiments completed ---")


if __name__ == "__main__":
    main()
