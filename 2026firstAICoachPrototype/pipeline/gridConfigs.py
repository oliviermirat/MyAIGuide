import numpy as np
from typing import Dict, List


# Hyperparameter grids (data-version independent)
CONFIG_GRID_DEBUG: Dict[str, List] = {
    "ACUTE_WINDOW": [15],
    "CHRONIC_WINDOW": [35],
    "ONLY_USE_ACWR": [False],
    "INCLUDE_NB_PREVIOUS_DAY_PAIN": [0],
    "SEEK_MOST_IMPORTANT_FEATURES": [True],
    "NB_TOP_FEATURES_TO_KEEP": [5],
    "HIGH_PAIN_QUARTILE_DEFINITION": [0.7],
    "WARNING_WINDOW": [1],
}

CONFIG_GRID_STANDARD: Dict[str, List] = {
    "ACUTE_WINDOW": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19],
    "CHRONIC_WINDOW": [21, 28, 35, 42, 49],
    "ONLY_USE_ACWR": [False],
    "INCLUDE_NB_PREVIOUS_DAY_PAIN": [0],
    "SEEK_MOST_IMPORTANT_FEATURES": [True],
    "NB_TOP_FEATURES_TO_KEEP": [5, 10],
    "HIGH_PAIN_QUARTILE_DEFINITION": [0.7, 0.8, 0.9, 0.95],
    "WARNING_WINDOW": [1],
}


def _build_candidate_config_for_new() -> Dict[str, Dict[str, List[str]]]:
    """
    Candidate variable groups for the NEW dataset (after May 2023).
    """
    rest = ["score"]

    physicalLoadKnee = [
        "numberOfSteps",
        "manicTimeRealTime",
        "timeSpentDriving",
        "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling",
    ]

    physicalLoadFace = [
        "manicTimeRealTime",
        "timeSpentDriving",
        "timeSpentRidingCar",
        "phoneTime",
    ]

    physicalLoadArm = [
        "numberOfComputerClicksAndKeyStrokes",
        "surfCumBpmAbove110",
        "numberOfHeartBeatsAbove110_upperBodyActivity",
        "climbingMaxEffortIntensity"
    ]

    all_variables = np.unique(physicalLoadKnee + physicalLoadFace + physicalLoadArm)
    all_variables = [str(all_variables[i]) for i in range(len(all_variables))]

    return {
        "kneePain": {
            "physicalLoad": physicalLoadKnee,
            "allVariables": all_variables,
        },
        "facePain": {
            "physicalLoad": physicalLoadFace,
            "allVariables": all_variables,
        },
        "armPain": {
            "physicalLoad": physicalLoadArm,
            "allVariables": all_variables,
        },
    }


def _build_candidate_config_for_old() -> Dict[str, Dict[str, List[str]]]:
    """
    Candidate variable groups for the OLD dataset (before May 2023).
    """
    rest = ["score"]

    physicalLoadKnee = [
        "tracker_mean_distance",
        "manicTimeDelta_corrected",
        "timeDrivingCar",
        "cycling",
    ]

    physicalLoadFace = [
        "manicTimeDelta_corrected",
        "timeDrivingCar",
    ]

    physicalLoadArm = [
        "whatPulseT_corrected",
        "surfing",
        "swimmingKm",
        "climbingMaxEffortIntensity",
    ]

    all_variables = np.unique(physicalLoadKnee + physicalLoadFace + physicalLoadArm)
    all_variables = [str(all_variables[i]) for i in range(len(all_variables))]

    return {
        "kneePain": {
            "physicalLoad": physicalLoadKnee,
            "allVariables": all_variables,
        },
        "foreheadEyesPain": {
            "physicalLoad": physicalLoadFace,
            "allVariables": all_variables,
        },
        "fingerHandArmPain": {
            "physicalLoad": physicalLoadArm,
            "allVariables": all_variables,
        },
    }


def get_candidate_config(data_version: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Return CONFIG_GRID_CANDIDATES for the requested data version.

    data_version: 'new' or 'old'
    """
    if data_version == "new":
        print("Using NEW data (after May 2023)")
        return _build_candidate_config_for_new()
    if data_version == "old":
        print("Using OLD data (before May 2023)")
        return _build_candidate_config_for_old()

    raise ValueError(f"Unsupported data_version '{data_version}'. Use 'new' or 'old'.")


# Backwards-compatible default (kept for direct script usage).
# The main run scripts should call get_candidate_config(...) explicitly.
DEFAULT_DATA_VERSION = "new"
CONFIG_GRID_CANDIDATES = get_candidate_config(DEFAULT_DATA_VERSION)
