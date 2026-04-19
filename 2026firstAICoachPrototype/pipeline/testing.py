from libraries.featureEngineeringFunctions import featureEngineering
from libraries.evaluateRandomForest import plot_risk_by_pain_category, get_roc_auc
from libraries.trainRandomForest import randomForestTrain
from libraries.dataLoader import load_and_preprocess_data
from libraries.run_context import RunPaths, create_run_paths
from sklearn.preprocessing import MinMaxScaler
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import sys
import os


MAX_RED_ALERTS_PERCENT = 0.15
MAX_YELLOW_ALERTS_PERCENT = 0.5
TRAFFIC_LIGHT_PROB_COLOR = "#A8D8F0"
TRAFFIC_LIGHT_PROB_ALPHA = 0.5
SHOW_PLOT_MINMAX = False
SHOW_PLOT_MAXPAIN_CLIP_STANDARDSCALER = False
SILENT_MODE = 0
TEST_ON_TEST_DATASET = True


def run_testing_for_pain(
    pain_type: str,
    save_graph_dont_plot: bool,
    save_risk_by_category_dont_plot: bool,
    dfTrainAndVal: pd.DataFrame,
    dfTrain: pd.DataFrame,
    dfVal: pd.DataFrame,
    dfTest: pd.DataFrame,
    testingDataset: str,
    trainingDatasetJustBeforeTesting: str,
    run_paths: RunPaths,
) -> None:
    """
    Run evaluation of the already-optimized model on validation/test data.
    """
    # Load best parameters found for training (found on training set)
    json_filename = run_paths.output_dir / f"best_params_{pain_type}.json"
    try:
        with json_filename.open("r") as f:
            params = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Could not find {json_filename}. Run training/grid search first.")
        sys.exit(1)

    # Training model
    if trainingDatasetJustBeforeTesting == "train_val":
        model, evaluationMetrics, top_features = randomForestTrain(
            dfTrainAndVal,
            pain_type,
            params,
            SILENT_MODE,
            TEST_ON_TEST_DATASET,
            figures_dir=run_paths.figures_dir,
        )
    else:
        model, evaluationMetrics, top_features = randomForestTrain(
            dfTrain,
            pain_type,
            params,
            SILENT_MODE,
            TEST_ON_TEST_DATASET,
            figures_dir=run_paths.figures_dir,
        )

    acute_window = int(params["ACUTE_WINDOW"])
    chronic_window = int(params["CHRONIC_WINDOW"])
    candidates = params["CANDIDATES"]
    only_use_acwr = bool(params["ONLY_USE_ACWR"])
    include_nb_previous_day_pain = int(params["INCLUDE_NB_PREVIOUS_DAY_PAIN"])

    # Feature engineering then running the model on test set
    if testingDataset == "val":
        dfVal_fe, _ = featureEngineering(
            dfVal.copy(),
            candidates,
            only_use_acwr,
            acute_window,
            chronic_window,
            include_nb_previous_day_pain,
            pain_type,
        )
        X_test = dfVal_fe[top_features].copy()
        results = dfVal_fe[[pain_type]].copy()
    else:
        dfTest_fe, _ = featureEngineering(
            dfTest.copy(),
            candidates,
            only_use_acwr,
            acute_window,
            chronic_window,
            include_nb_previous_day_pain,
            pain_type,
        )
        X_test = dfTest_fe[top_features].copy()
        results = dfTest_fe[[pain_type]].copy()

    results.loc[:, "predictedProbsWarning"] = model.predict_proba(X_test)[:, 1]

    # Beginning of file doesn't have proper averaging over long enough duration
    results = results.iloc[chronic_window:]

    # Plotting results
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

    plt.figure(figsize=(20, 8))
    plt.plot(scaled_values)
    if save_graph_dont_plot:
        raw_preds_path = run_paths.figures_dir / f"rawPreds_{pain_type}.png"
        plt.savefig(raw_preds_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    # Generate Traffic Light Signals
    probs = results["predictedProbsWarning"].copy()
    sorted_probs = np.sort(probs)
    red_thresh = sorted_probs[int(len(sorted_probs) * (1 - MAX_RED_ALERTS_PERCENT))]
    yellow_thresh = sorted_probs[int(len(sorted_probs) * (1 - MAX_YELLOW_ALERTS_PERCENT))]

    pain_scaled = scaled_values[:, 0]
    risk_probs = results["predictedProbsWarning"].values

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
        prob = risk_probs[i + 1]
        if prob >= red_thresh:
            c = "red"
        elif prob >= yellow_thresh:
            c = "orange"
        else:
            c = "green"
        ax1.plot(
            [i, i + 1],
            [pain_scaled[i], pain_scaled[i + 1]],
            color=c,
            linewidth=2,
            zorder=2,
        )

    ax1.set_title(f"{pain_type} (MinMax Scaled) Colored by Next Day's Risk Prediction")
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
        traffic_path = run_paths.figures_dir / f"trafficLights_{pain_type}.png"
        fig.savefig(traffic_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    evaluationMetrics = get_roc_auc(results, pain_type)
    print("Evaluation metrics:", evaluationMetrics)


def _cli_main() -> None:
    """
    Entry point for running testing.py directly from the console.
    """
    # First argument should be 'kneePain', 'facePain' or 'armPain'
    pain_type = sys.argv[1]
    save_graph_dont_plot = bool(int(sys.argv[2])) if len(sys.argv) >= 3 else False
    save_risk_by_category_dont_plot = bool(int(sys.argv[3])) if len(sys.argv) >= 4 else False

    file_path = sys.argv[4]
    stressorVarsMinMaxScaler = int(sys.argv[5])
    painRemoveOutliers = int(sys.argv[6])
    split_percent_trainval_test = float(sys.argv[7])
    split_percent_train_val = float(sys.argv[8])
    testingDataset = sys.argv[9]
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

    run_testing_for_pain(
        pain_type=pain_type,
        save_graph_dont_plot=save_graph_dont_plot,
        save_risk_by_category_dont_plot=save_risk_by_category_dont_plot,
        dfTrainAndVal=dfTrainAndVal,
        dfTrain=dfTrain,
        dfVal=dfVal,
        dfTest=dfTest,
        testingDataset=testingDataset,
        trainingDatasetJustBeforeTesting=trainingDatasetJustBeforeTesting,
        run_paths=run_paths,
    )


if __name__ == "__main__":
    _cli_main()
