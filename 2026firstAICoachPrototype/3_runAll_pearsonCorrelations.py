import numpy as np
import pandas as pd
import pickle
from scipy.stats import pearsonr
from sklearn.preprocessing import MinMaxScaler

from libraries.run_context import RESULTS_ROOT

FILE_PATH = "newDataset.pkl"
OUTPUT_DIR = RESULTS_ROOT / "combinedAnalysis" / "pearsonCorrelations"

with open(FILE_PATH, "rb") as f:
    data = pickle.load(f)

# Ensure datetime index
data.index = pd.to_datetime(data.index)

lags = {
    "past_15_days": [i for i in range(0, 16)],
    "past_35_days": [i for i in range(0, 36)]
}

columnsOfInterest = ['numberOfSteps', 'surfCumBpmAbove110', 'phoneTime', 'manicTimeRealTime', 'climbingMaxEffortIntensity', 'kneePain', 'armPain', 'facePain', 'cyclingCalories', 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling', 'timeSpentDriving', 'numberOfComputerClicksAndKeyStrokes', 'numberOfHeartBeatsAbove110_upperBodyActivity', 'generalMood']

correlationsOfInterest = {
  'facePain': ['phoneTime', 'manicTimeRealTime', 'timeSpentDriving', 'generalMood'],
  'kneePain': ['manicTimeRealTime', 'numberOfSteps', 'cyclingCalories', 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling', 'timeSpentDriving', 'generalMood'],
  'armPain':  ['surfCumBpmAbove110', 'climbingMaxEffortIntensity', 'numberOfComputerClicksAndKeyStrokes', 'numberOfHeartBeatsAbove110_upperBodyActivity', 'generalMood'],
  'manicTimeRealTime': ['cyclingCalories', 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling', 'numberOfComputerClicksAndKeyStrokes'],
  'numberOfComputerClicksAndKeyStrokes': ['cyclingCalories'],
  'cyclingCalories': ['manicTimeRealTime', 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling', 'numberOfComputerClicksAndKeyStrokes'],
  'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling': ['manicTimeRealTime', 'cyclingCalories']
 }

results = []
specific_results = [] # New list to store only the correlations of interest

for col1 in columnsOfInterest:
    for col2 in columnsOfInterest:
        if col1 == col2:
            continue
        acute = pd.concat([data[col2].shift(lag) for lag in lags["past_15_days"]], axis=1).mean(axis=1)
        chronic = pd.concat([data[col2].shift(lag) for lag in lags["past_35_days"]], axis=1).mean(axis=1)
        acwr = (acute / chronic.replace(0, np.nan)).fillna(0)
        lag_series = {
            "past_15_days": acute,
            "past_35_days": chronic,
            "past_acwr": acwr,
        }
        for lag_label, shifted in lag_series.items():
            valid = data[col1].notna() & shifted.notna()
            x = data[col1][valid]
            y = shifted[valid]

            if len(x) > 2:
                corr, pval = pearsonr(x, y)
                results.append({
                    "Variable_1": col1,
                    "Variable_2": col2,
                    "Lag": lag_label,
                    "Correlation": corr,
                    "P-value": pval,
                    "Significant (p < 0.05)": pval < 0.05
                })
            
            # Print and save the specific correlations of interest
            if (col1 in correlationsOfInterest) and (col2 in correlationsOfInterest[col1]):
                is_significant = pval < 0.05
                # print(is_significant, col1, col2, lag_label, corr, pval)
                
                # Append to our new list
                specific_results.append({
                    "Significant (p < 0.05)": is_significant,
                    "Variable_1": col1,
                    "Variable_2": col2,
                    "Lag": lag_label,
                    "Correlation": corr,
                    "P-value": pval
                })

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
if specific_results:
    specific_df = pd.DataFrame(specific_results)
    specific_df.to_excel(OUTPUT_DIR / "correlations_of_interest_output.xlsx", index=False)