"""
Run ensemble inference (pipeline.testing2_ensemble) on an extended .pkl dataset.

Hyperparameters come from the ranked rows in an existing grid-search summary
(e.g. results/baseline/hyperparametersGridSearchResults/summaryResults.xlsx).
Only the top N ensemble models are trained — no full hyperparameter grid.

Outputs (plots, traffic-light xlsx) go under results/<OUTPUT_RUN_NAME>/bestHyperparametersSetResults/.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

import pandas as pd

from libraries.dataLoader import load_and_preprocess_data
from libraries.run_context import (
    RESULTS_ROOT,
    SUMMARY_RESULTS_XLSX,
    RunPaths,
    create_run_paths,
)
import pipeline.testing2_ensemble as testing2_ensemble
from pipeline.testing2_ensemble import (
    TRAFFIC_LIGHT_PAIN_REGION_COLUMNS,
    run_testing2_for_pain,
    save_traffic_light_percent_excel,
)

# --- Configuration (match 2_baseline.py unless noted) ---

BASELINE_RUN_NAME = "baseline"

EXTENDED_FILE_PATH = "dataMay2023andLater_2026firstAIPrototype.pkl"

N_ENSEMBLE_MODELS = 15

STRESSOR_VARS_MINMAX_SCALER = 0
PAIN_REMOVE_OUTLIERS = 0
SPLIT_PERCENT_TRAINVAL_TEST = 0.553 # This 0.553 is to match the subsets below #0.75
# dfTrain: 2023-05-15 to 2024-08-02
# dfVal:   2024-08-03 to 2025-02-10
# dfTest:  2025-02-11 to 2025-09-11 and beyond
SPLIT_PERCENT_TRAIN_VAL = 0.7
TRAINING_DATASET_BEFORE_TESTING = "train_val"

PAIN_TYPES = ["kneePain", "facePain", "armPain"]

SAVE_GRAPHS_DONT_PLOT = True
SAVE_RISK_BY_CATEGORY_DONT_PLOT = True

TIME_ON_COMPUTER_SCALE_AFTER_DATE = "2025-11-01"


def create_inference_run_paths(
    summary_run_name: str,
    output_run_name: str,
) -> RunPaths:
    """
    Read summaryResults.xlsx from the baseline (summary) run, write figures to output run.
    """
    summary_paths = create_run_paths(summary_run_name)
    output_paths = create_run_paths(output_run_name)
    return RunPaths(
        base_dir=output_paths.base_dir,
        output_dir=summary_paths.output_dir,
        figures_dir=output_paths.figures_dir,
    )


def print_split_cutoff_dates(
    df_train,
    df_val,
    df_test,
    *,
    split_percent_trainval_test: float,
    split_percent_train_val: float,
) -> None:
    """Print inclusive date ranges and split cut-offs for train / val / test."""
    print("")
    print("=== Dataset split dates (extended pickle) ===")
    print(
        f"Training set:   {df_train.index[0]}  →  {df_train.index[-1]}  "
        f"({len(df_train)} days)"
    )
    print(
        f"Validation set: {df_val.index[0]}  →  {df_val.index[-1]}  "
        f"({len(df_val)} days)"
    )
    print(
        f"Test set:       {df_test.index[0]}  →  {df_test.index[-1]}  "
        f"({len(df_test)} days)"
    )
    print("")
    print("Split cut-off dates (first day of the next segment):")
    print(f"  Train → validation:  {df_val.index[0]}")
    print(f"  Validation → test:   {df_test.index[0]}")
    print("")
    print(
        f"Split fractions: train+val vs test = {split_percent_trainval_test:.2f}, "
        f"train vs val (within train+val) = {split_percent_train_val:.2f}"
    )
    print(
        f"Last training day:   {df_train.index[-1]}  |  "
        f"Last validation day: {df_val.index[-1]}"
    )


def _resolve_summary_path(run_paths: RunPaths) -> Path:
    return run_paths.output_dir / SUMMARY_RESULTS_XLSX


def main() -> None:
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run ensemble inference with scaling parameters.")
    parser.add_argument("--file_path", type=str, default=EXTENDED_FILE_PATH, help="Path to the extended .pkl dataset")
    parser.add_argument("--output_run_name", type=str, default="extendedTestSet", help="Output directory name")
    parser.add_argument("--apply_scaling", action="store_true", help="Flag to apply time scaling")
    parser.add_argument("--multiplier", type=float, default=0.75, help="Multiplier for time on computer")
    
    args = parser.parse_args()

    # Assign parsed arguments to variables used in the script
    file_path = args.file_path
    OUTPUT_RUN_NAME = args.output_run_name
    APPLY_TIME_ON_COMPUTER_SCALING = args.apply_scaling
    TIME_ON_COMPUTER_MULTIPLIER = args.multiplier

    pkl_path = Path(file_path)
    if not pkl_path.is_file():
        print(f"ERROR: Extended dataset not found: {pkl_path.resolve()}")
        sys.exit(1)

    testing2_ensemble.N_ENSEMBLE_MODELS_FOR_TEST_PROBS = N_ENSEMBLE_MODELS

    # The rest of your main() function remains exactly the same below this point...
    run_paths = create_inference_run_paths(BASELINE_RUN_NAME, OUTPUT_RUN_NAME)
    # ...
    
    # file_path = sys.argv[1] if len(sys.argv) > 1 else EXTENDED_FILE_PATH
    # pkl_path = Path(file_path)
    # if not pkl_path.is_file():
        # print(f"ERROR: Extended dataset not found: {pkl_path.resolve()}")
        # print(f"Usage: python {Path(__file__).name} [path/to/extended.pkl]")
        # sys.exit(1)

    # testing2_ensemble.N_ENSEMBLE_MODELS_FOR_TEST_PROBS = N_ENSEMBLE_MODELS

    run_paths = create_inference_run_paths(BASELINE_RUN_NAME, OUTPUT_RUN_NAME)
    summary_path = _resolve_summary_path(run_paths)
    if not summary_path.is_file():
        print(
            f"ERROR: Missing grid-search summary at {summary_path.resolve()}. "
            f"Run 2_baseline.py (or equivalent) for run '{BASELINE_RUN_NAME}' first."
        )
        sys.exit(1)

    summary_df = pd.read_excel(summary_path)
    n_models = min(N_ENSEMBLE_MODELS, len(summary_df))
    if n_models < 1:
        print(f"ERROR: {summary_path} has no rows.")
        sys.exit(1)

    print("")
    print(f"Extended dataset: {pkl_path.resolve()}")
    print(f"Ensemble hyperparameters from: {summary_path.resolve()}")
    print(
        f"Using top {n_models} ranked row(s) from summaryResults "
        f"(N_ENSEMBLE_MODELS={N_ENSEMBLE_MODELS}); training {n_models} models per pain type only."
    )
    print(f"Writing outputs to: {run_paths.figures_dir.resolve()}")

    df_train_and_val, df_train, df_val, df_test = load_and_preprocess_data(
        str(pkl_path),
        SPLIT_PERCENT_TRAINVAL_TEST,
        STRESSOR_VARS_MINMAX_SCALER,
        PAIN_REMOVE_OUTLIERS,
        SPLIT_PERCENT_TRAIN_VAL,
    )
    
    df_test = df_test[:'2026-06-25']
    if APPLY_TIME_ON_COMPUTER_SCALING:
        column = "manicTimeRealTime"
        cutoff = pd.Timestamp(TIME_ON_COMPUTER_SCALE_AFTER_DATE)
        dates = pd.to_datetime(df_test.index)
        mask = dates > cutoff
        df_test.loc[mask, column] = df_test.loc[mask, column] * TIME_ON_COMPUTER_MULTIPLIER
    
    print_split_cutoff_dates(
        df_train,
        df_val,
        df_test,
        split_percent_trainval_test=SPLIT_PERCENT_TRAINVAL_TEST,
        split_percent_train_val=SPLIT_PERCENT_TRAIN_VAL,
    )

    pct_red_tl = []
    pct_yellow_tl = []
    for pain_type in PAIN_TYPES:
        pr, py = run_testing2_for_pain(
            pain_type=pain_type,
            save_graph_dont_plot=SAVE_GRAPHS_DONT_PLOT,
            save_risk_by_category_dont_plot=SAVE_RISK_BY_CATEGORY_DONT_PLOT,
            dfTrainAndVal=df_train_and_val,
            dfTrain=df_train,
            dfTest=df_test,
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

    print("")
    print(
        f"--- Extended-test ensemble inference finished "
        f"(results under {RESULTS_ROOT / OUTPUT_RUN_NAME}) ---"
    )


if __name__ == "__main__":
    main()
