import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import argrelextrema
import scipy.stats as stats
import pandas as pd
from numpy.linalg import inv
import xlsxwriter
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import pearsonr

startDate = '2016-01-01'
endDate = '2022-03-26'
rolling_window = 7
threshold_r = 0.3
partial_r_threshold = 0.025
globalMeasureCalculation = 'max_minus_min'
useNewOrOldData = 'old'

# Load previously saved cross-correlation data
with open("crosscorrelation_plots_" + useNewOrOldData + "/crosscorrelation_data.pkl", "rb") as f:
    data = pickle.load(f)

# Helper to compute local and global measures
def compute_measures(lags, corrs, integral_half_window=30):
    lags = np.array(lags)
    corrs = np.array(corrs)
    zero_idx = np.where(lags == 0)[0][0] if 0 in lags else np.argmin(np.abs(lags))

    local_max_idx = argrelextrema(corrs, np.greater)[0]
    local_min_idx = argrelextrema(corrs, np.less)[0]

    left_extremum_idx = next((i for i in reversed(range(zero_idx)) if i in local_max_idx or i in local_min_idx), None)
    right_extremum_idx = next((i for i in range(zero_idx, len(lags)) if i in local_max_idx or i in local_min_idx), None)

    local_measure = 0
    if left_extremum_idx is not None and right_extremum_idx is not None:
        left_val = corrs[left_extremum_idx]
        right_val = corrs[right_extremum_idx]
        denom = right_extremum_idx - left_extremum_idx
        if denom != 0:
            if left_val > right_val:
                local_measure = (zero_idx - right_extremum_idx) / denom
            elif left_val < right_val:
                local_measure = (zero_idx - left_extremum_idx) / denom

    neg_integral = np.trapz(corrs[zero_idx - integral_half_window:zero_idx], lags[zero_idx - integral_half_window:zero_idx])
    pos_integral = np.trapz(corrs[zero_idx + 1:zero_idx + 1 + integral_half_window], lags[zero_idx + 1:zero_idx + 1 + integral_half_window])

    if globalMeasureCalculation == 'max_minus_min':
        global_measure = pos_integral - neg_integral
    elif globalMeasureCalculation == 'only_max':
        global_measure = pos_integral
    elif globalMeasureCalculation == 'peak':
        positive_mask = lags > 0
        global_measure = np.max(corrs[positive_mask]) if np.any(positive_mask) else np.nan

    return local_measure, global_measure

# === PARTIAL CORRELATION FUNCTION ===
def compute_partial_corr(x, y, controls):
    if controls.shape[1] == 0:
        return pearsonr(x, y)[0]
    x_resid = sm.OLS(x, sm.add_constant(controls)).fit().resid
    y_resid = sm.OLS(y, sm.add_constant(controls)).fit().resid
    return pearsonr(x_resid, y_resid)[0]

# === PER-WINDOW FILTERING ===
print("🔍 Running per-window partial correlation filtering...")

filtered_data = []
for entry in data:
    var = entry['var']
    pain = entry['pain']
    start = entry['start']
    end = entry['end']

    try:
        with open("../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb") as f:
            full_data = pickle.load(f)
    except Exception as e:
        print("Failed to load raw data:", e)
        continue

    full_data = full_data[(full_data.index >= start) & (full_data.index <= end)]
    full_data = full_data.rolling(rolling_window).mean().dropna()

    if var not in full_data.columns or pain not in full_data.columns:
        continue

    x = full_data[var]
    y = full_data[pain]
    valid_xy = x.notna() & y.notna()
    if valid_xy.sum() < 5:
        continue

    x = x[valid_xy]
    y = y[valid_xy]

    control_vars = []
    for other_var in full_data.columns:
        if other_var in (var, pain):
            continue
        x1 = full_data[other_var]
        x2 = full_data[var]
        valid = x1.notna() & x2.notna()
        if valid.sum() < 2:
            continue
        r, _ = pearsonr(x1[valid], x2[valid])
        if abs(r) >= threshold_r:
            control_vars.append(other_var)

    controls = full_data[control_vars].loc[valid_xy].values if control_vars else np.empty((len(x), 0))
    partial_r = compute_partial_corr(x.values, y.values, controls)

    if abs(partial_r) >= partial_r_threshold:
        filtered_data.append(entry)
    else:
        print(f"🧹 Removed {var} (pain={pain}, {start.date()}–{end.date()}) — partial r={partial_r:.3f}")

# === ORGANIZE FINAL RESULTS ===
results_by_pain = {}
for entry in filtered_data:
    pain = entry['pain']
    var = entry['var']
    local, global_ = compute_measures(entry['lags'], entry['corrs'])
    integral = entry.get('integral', 1)

    if pain not in results_by_pain:
        results_by_pain[pain] = []
    results_by_pain[pain].append({
        'var': var,
        'local_measure': local,
        'global_measure': global_,
        'integral': integral
    })

all_pains = sorted(list(results_by_pain.keys()))
all_global_measures = [r['global_measure'] for plist in results_by_pain.values() for r in plist]

if not all_global_measures:
    print("❌ No variables passed per-window partial correlation filtering. Exiting early.")
    exit()

max_abs_global = max(abs(min(all_global_measures)), abs(max(all_global_measures)))

# === Continue with analysis, plots, statistics, etc. ===
