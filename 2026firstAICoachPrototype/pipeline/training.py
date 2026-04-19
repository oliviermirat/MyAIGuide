from libraries.featureEngineeringFunctions import featureEngineering
from libraries.evaluateRandomForest import get_roc_auc
from libraries.trainRandomForest import randomForestTrain
from libraries.dataLoader import load_and_preprocess_data
from libraries.run_context import RunPaths, create_run_paths
from .gridConfigs import CONFIG_GRID_DEBUG, CONFIG_GRID_STANDARD, get_candidate_config
import pandas as pd
import itertools
import sys
import os
from typing import Dict


SHOW_PLOT_MINMAX = False
SHOW_PLOT_MAXPAIN_CLIP_STANDARDSCALER = False
SILENT_MODE = 1


def run_grid_search_for_pain(
    pain_type: str,
    grid_template: Dict,
    candidates_config: Dict[str, Dict],
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    test_on_val_dataset: bool,
    include_all_candidate_sets: bool,
    run_paths: RunPaths,
) -> pd.DataFrame:
    """
    Run the Random Forest grid search for a single pain type.

    Returns the full results dataframe (one row per hyperparameter combination).
    """
    grid = dict(grid_template)  # shallow copy

    candidate_sets = [candidates_config[pain_type]["physicalLoad"]]
    if include_all_candidate_sets:
        candidate_sets.append(candidates_config[pain_type]["allVariables"])

    grid["CANDIDATES"] = candidate_sets
    keys, values = zip(*grid.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print(f"Starting Grid Search for {pain_type}: {len(combinations)} combinations.")

    results_data = []

    header = list(grid.keys()) + [
        "top",
        "nb_top",
        "std_top",
        "bottom",
        "nb_bottom",
        "corr_coeff",
        "p_val_corr_coeff",
        "custom_score",
    ]

    for i, params in enumerate(combinations):
        print(f"Running iteration {i + 1}/{len(combinations)}...")

        try:
            model, evaluation_metrics, top_features = randomForestTrain(
                df_train,
                pain_type,
                params,
                SILENT_MODE,
                test_on_val_dataset,
                figures_dir=run_paths.figures_dir,
            )

            if test_on_val_dataset:
                df_val_fe, _ = featureEngineering(
                    df_val.copy(),
                    params["CANDIDATES"],
                    params["ONLY_USE_ACWR"],
                    params["ACUTE_WINDOW"],
                    params["CHRONIC_WINDOW"],
                    params["INCLUDE_NB_PREVIOUS_DAY_PAIN"],
                    pain_type,
                )

                X_test = df_val_fe[top_features].copy()
                results = df_val_fe[[pain_type]].copy()
                results.loc[:, "predictedProbsWarning"] = model.predict_proba(
                    X_test
                )[:, 1]

                # Beginning of file doesn't have proper averaging over long enough duration
                results = results.iloc[params["CHRONIC_WINDOW"] :]

                evaluation_metrics = get_roc_auc(results, pain_type)

            row = list(params.values()) + list(evaluation_metrics.values())
            results_data.append(row)

        except Exception as e:
            print(f"Error on iteration {i}: {e}")

    results_df = pd.DataFrame(results_data, columns=header)

    sorted_results = results_df.sort_values(by="custom_score", ascending=False)
    output_file = run_paths.output_dir / f"sorted_results_{pain_type}.csv"
    sorted_results.to_csv(output_file, index=False)

    print(f"Saved sorted grid search results to {output_file}")

    return sorted_results


def _cli_main() -> None:
    """
    Entry point when calling this script directly from the console.
    Keeps backwards compatibility with the previous CLI usage.
    """
    # First argument should be 'kneePain', 'facePain' or 'armPain'
    pain_type = sys.argv[1]

    # Second argument should be 'CONFIG_GRID_DEBUG' or 'CONFIG_GRID_STANDARD'
    grid_config_name = sys.argv[2]
    test_on_val_dataset = bool(int(sys.argv[3]))

    file_path = sys.argv[4]
    stressorVarsMinMaxScaler = int(sys.argv[5])
    painRemoveOutliers = int(sys.argv[6])
    split_percent_trainval_test = float(sys.argv[7])
    split_percent_train_val = float(sys.argv[8])

    # Optional: whether to include 'allVariables' in addition to 'physicalLoad'
    include_all_candidate_sets = True
    if len(sys.argv) > 9:
        include_all_candidate_sets = bool(int(sys.argv[9]))

    # Optional: run name to route grid-search vs best-hyperparameter outputs under results/<run>/
    run_name = sys.argv[10] if len(sys.argv) > 10 else None

    dfTrainAndVal, dfTrain, dfVal, dfTest = load_and_preprocess_data(
        file_path,
        split_percent_trainval_test,
        stressorVarsMinMaxScaler,
        painRemoveOutliers,
        split_percent_train_val,
    )

    run_paths = create_run_paths(run_name)

    if grid_config_name == "CONFIG_GRID_DEBUG":
        grid_template = CONFIG_GRID_DEBUG
    elif grid_config_name == "CONFIG_GRID_STANDARD":
        grid_template = CONFIG_GRID_STANDARD
    else:
        raise ValueError(
            "grid_config_name must be 'CONFIG_GRID_DEBUG' or 'CONFIG_GRID_STANDARD'"
        )

    # For direct CLI usage we default to the NEW dataset configuration.
    candidates_config = get_candidate_config("new")

    run_grid_search_for_pain(
        pain_type=pain_type,
        grid_template=grid_template,
        candidates_config=candidates_config,
        df_train=dfTrain,
        df_val=dfVal,
        test_on_val_dataset=test_on_val_dataset,
        include_all_candidate_sets=include_all_candidate_sets,
        run_paths=run_paths,
    )


if __name__ == "__main__":
    _cli_main()
