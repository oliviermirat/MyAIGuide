from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pickle
import os
from datetime import timedelta
from scipy.signal import argrelextrema

# --- Parameters ---
rolling_window = 7
max_lag = 50
useNewOrOldData = 'old' #'new'  # or 'old'
if useNewOrOldData == 'old':
  startDate = '2016-05-01'
  endDate   = '2021-09-01'
  # startDate = '2016-01-01'
  # endDate   = '2022-03-26'
else:
  startDate = '2023-05-15'
  endDate   = '2024-09-15'
  # startDate = '2023-05-15'
  # endDate = '2025-04-29'
  
keepOnlyNbHighIntegral = 0
stressors_to_include = []  # Optional filtering
look_at_positive_lags_only = False
use_nearest_lag_to_zero = False
plot_by_variable_across_time = True
plot_variable_subplots = True
monthWindow = 6
monthShift = 2

# --- Load data ---
if useNewOrOldData == 'new':
    with open("../../dataMay2023andLater.pkl", "rb") as f:
        data = pickle.load(f)
    data['movingBadSuitcase'] = 0
    data.loc['2025-01-10', 'movingBadSuitcase'] = 10
    data.loc['2025-01-11', 'movingBadSuitcase'] = 20
    data.loc['2025-01-12', 'movingBadSuitcase'] = 5
    data.loc['2025-01-18', 'movingBadSuitcase'] = 3
    data.loc['2025-01-19', 'movingBadSuitcase'] = 1
    data.loc['2025-01-20', 'movingBadSuitcase'] = 1
    data.loc['2025-01-21', 'movingBadSuitcase'] = 1
    data.loc['2025-01-22', 'movingBadSuitcase'] = 3
    data.loc['2025-01-24', 'movingBadSuitcase'] = 6
    data.loc['2025-01-25', 'movingBadSuitcase'] = 2
    pain_variables = ['kneePain', 'armPain', 'facePain']
else:
    with open("../../../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb") as f:
        data = pickle.load(f)
    
    data = data.drop(columns=[
        'sick_tired', 'painInOtherRegion', 'foreheadPain', 'eyesPain',
        'shoulderPain', 'elbowPain', 'generalmood', 'handsAndFingerPain',
        'forearmElbowPain', 'shoulderNeckPain', 'foreheadAndEyesPain',
        'aroundEyesPain', 'fingerHandArmPain', 'fingersPain'])
    print(data.columns)
    pain_variables = ['kneePain', 'foreheadEyesPain', 'wholeArm']

# --- Filter and smooth data ---
data = data[(data.index >= startDate) & (data.index <= endDate)]

if True:
    data = data.apply(
        lambda col: col.rolling('180D', min_periods=1).apply(
            lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0,
            raw=False
        )
    )

if False:
  data = data.rolling(rolling_window).mean().dropna()



from scipy.stats import pearsonr

# Ensure datetime index
data.index = pd.to_datetime(data.index)

# Define lag windows
lags = {
    "same_day": [0],
    "next_day": [1],
    "next_2_days": [1, 2],
    "next_3_days": [1, 2, 3],
    "next_4_days": [1, 2, 3, 4],
    "next_5_days": [1, 2, 3, 4, 5]
}

# lags = {
    # "same_day": [0],
    # "next_day": [1],
    # "next_2_days": [1, 2],
    # "next_3_days": [1, 2, 3],
    # "next_4_days": [1, 2, 3, 4],
    # "next_30_days": [i for i in range(0, 31)]
# }

# Store results
results = []

for col1 in data.columns:
    for col2 in data.columns:
        if col1 == col2:
            continue
        for lag_label, lag_days in lags.items():
            shifted = pd.concat(
                [data[col2].shift(-lag) for lag in lag_days],
                axis=1
            ).mean(axis=1)

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

# Convert to DataFrame
signif_df = pd.DataFrame(results)

# Filter significant correlations
significant_only = signif_df[signif_df["Significant (p < 0.05)"]]

# Sort by descending correlation (not abs)
significant_only_sorted = significant_only.sort_values(by="Correlation", ascending=False)

# Save sorted results
significant_only_sorted.to_csv("significant_correlations_sorted.csv", index=False)

# Filter to only pain-related Variable_2
if useNewOrOldData == 'old':
  pain_vars = ["kneePain", "wholeArm", "foreheadEyesPain"]
else:
  pain_vars = ["kneePain", "armPain", "facePain"]
# pain_related = significant_only_sorted[significant_only_sorted["Variable_2"].isin(pain_vars)]
pain_related = significant_only_sorted[
    significant_only_sorted["Variable_2"].isin(pain_vars) &
    ~significant_only_sorted["Variable_1"].isin(pain_vars)
]

# Save pain-related results
pain_related.to_csv("significant_correlations_pain_only.csv", index=False)

# Group by (Variable_1, Variable_2) pairs
grouped = pain_related.groupby(["Variable_1", "Variable_2"])

# Select the row with correlation closest to +1 and -1 for each group
closest_to_1 = grouped.apply(
    lambda g: g[g["Correlation"] > 0].loc[(g["Correlation"] - 1).abs().idxmin()] if any(g["Correlation"] > 0) else None
).dropna().reset_index(drop=True)

closest_to_minus1 = grouped.apply(
    lambda g: g[g["Correlation"] < 0].loc[(g["Correlation"] + 1).abs().idxmin()] if any(g["Correlation"] < 0) else None
).dropna().reset_index(drop=True)

# Combine and drop duplicates (in case +1 and -1 are the same)
extreme_corrs = pd.concat([closest_to_1, closest_to_minus1]).drop_duplicates()

# Optional: sort for readability
extreme_corrs_sorted = extreme_corrs.sort_values(by=["Variable_2", "Correlation"], ascending=[True, False])

# Save to Excel or CSV
extreme_corrs_sorted.to_csv("extreme_significant_pain_correlations.csv", index=False)

# Optional: show a few rows
print("\nMost extreme positive/negative correlations per Variable_1 → pain pair:")
print(extreme_corrs_sorted.head(10))


