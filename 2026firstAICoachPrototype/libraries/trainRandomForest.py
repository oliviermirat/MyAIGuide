from libraries.featureEngineeringFunctions import featureEngineering
from sklearn.ensemble import RandomForestClassifier
from libraries.evaluateRandomForest import get_roc_auc
import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, Iterable, List, Union

from libraries.run_context import BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR


nbDaysPriors = 1


def _get_candidate_variables(
    df_train: pd.DataFrame,
    pain_type: str,
    params: Dict,
) -> pd.DataFrame:
    """
    Restrict the training dataframe to the candidate features and target.
    """
    candidate_cols: Iterable[str] = params["CANDIDATES"]
    return df_train[list(candidate_cols) + [pain_type]].copy()


def randomForestTrain(
    df_train: pd.DataFrame,
    pain_type: str,
    params: Dict,
    silent_mode: int,
    test_on_val_dataset: bool,
    figures_dir: Union[str, Path] = BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR,
):
    """
    Train a RandomForest model for a given pain type and hyperparameter set.

    The hyperparameters are provided via the `params` dictionary which should
    contain at least:
      - 'ACUTE_WINDOW'
      - 'CHRONIC_WINDOW'
      - 'SEEK_MOST_IMPORTANT_FEATURES'
      - 'NB_TOP_FEATURES_TO_KEEP'
      - 'HIGH_PAIN_QUARTILE_DEFINITION'
      - 'WARNING_WINDOW'
      - 'CANDIDATES'
      - 'ONLY_USE_ACWR'
      - 'INCLUDE_NB_PREVIOUS_DAY_PAIN'
    """
    acute_window = params["ACUTE_WINDOW"]
    chronic_window = params["CHRONIC_WINDOW"]
    seek_most_important = params["SEEK_MOST_IMPORTANT_FEATURES"]
    nb_top_features = params["NB_TOP_FEATURES_TO_KEEP"]
    high_pain_quantile = params["HIGH_PAIN_QUARTILE_DEFINITION"]
    warning_window = params["WARNING_WINDOW"]
    candidates = params["CANDIDATES"]
    only_use_acwr = params["ONLY_USE_ACWR"]
    include_nb_previous_day_pain = params["INCLUDE_NB_PREVIOUS_DAY_PAIN"]

    df = _get_candidate_variables(df_train, pain_type, params)

    df, candidate_variables = featureEngineering(
        df.copy(),
        candidates,
        only_use_acwr,
        acute_window,
        chronic_window,
        include_nb_previous_day_pain,
        pain_type,
    )

    # Identifying high pain days
    threshold = df[pain_type].quantile(high_pain_quantile)
    if not silent_mode:
        print(f"High pain threshold found at {high_pain_quantile}:", threshold)

    is_high_pain = (df[pain_type] > threshold).astype(int)

    # A warning is accurate on the current day of high pain and up to
    # (warning_window - 1) days prior
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=warning_window)
    df[f"{pain_type}_warningCorrect"] = (
        is_high_pain.rolling(window=indexer).max().fillna(0)
    )

    # Finding most important features
    if seek_most_important:
        X_train_0 = df[candidate_variables]
        y_train_0 = df[f"{pain_type}_warningCorrect"]
        model_selector = RandomForestClassifier(
            n_estimators=200,
            max_depth=5,
            class_weight="balanced",
            random_state=42,
        )
        model_selector.fit(X_train_0, y_train_0.values.ravel())
        importances = pd.Series(
            model_selector.feature_importances_, index=X_train_0.columns
        ).sort_values(ascending=False)
        top_features: List[str] = importances.head(nb_top_features).index.tolist()

        if not silent_mode:
            print("top_features:", top_features)

        figures_path = Path(figures_dir)
        figures_path.mkdir(parents=True, exist_ok=True)
        top_features_file = figures_path / f"top_features_{pain_type}.txt"
        with top_features_file.open("w") as f:
            for feature in top_features:
                f.write(f"{feature}\n")
    else:
        top_features = candidate_variables

    X_train = df[top_features]
    y_train = df[f"{pain_type}_warningCorrect"]

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train.values.ravel())

    if test_on_val_dataset:
        evaluation_metrics = {}
    else:
        # Generating results dataframe (evaluation on training dataset)
        results = df[[pain_type, f"{pain_type}_warningCorrect"]].copy()
        results.loc[:, "predictedProbsWarning"] = model.predict_proba(X_train)[:, 1]
        # Beginning doesn't have a large enough chronic window
        results = results.iloc[chronic_window:]
        evaluation_metrics = get_roc_auc(results, pain_type)

    return [model, evaluation_metrics, top_features]
