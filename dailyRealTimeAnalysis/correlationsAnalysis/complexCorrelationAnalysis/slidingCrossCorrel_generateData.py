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
# startDate = '2023-05-15'
# endDate = '2025-04-29'
startDate = '2016-01-01'
endDate   = '2022-03-26'
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
data = data.rolling(rolling_window).mean().dropna()

# --- Cross-correlation function ---
def cross_correlation(ts1, ts2, lags):
    corrs = []
    for lag in lags:
        shifted = ts1.shift(lag)
        valid = ts2.notna() & shifted.notna()
        if valid.sum() > 5:
            corrs.append(ts2[valid].corr(shifted[valid]))
        else:
            corrs.append(np.nan)
    return lags, corrs

lags = list(range(-max_lag, max_lag + 1))

all_vars = list(data.columns)
if stressors_to_include:
    stressor_vars = [var for var in stressors_to_include if var in all_vars]
else:
    stressor_vars = [v for v in all_vars if v not in pain_variables]

# --- Output setup ---
output_folder = "crosscorrelation_plots_" + useNewOrOldData
os.makedirs(output_folder, exist_ok=True)
crosscorr_results = []

# --- Sliding window setup ---
window_size = pd.DateOffset(months=monthWindow)
step_size = pd.DateOffset(months=monthShift)

start = pd.to_datetime(startDate)
end = pd.to_datetime(endDate)

while start + window_size <= end:
    print("start:", start)
    stop = start + window_size
    midpoint = start + (stop - start) / 2
    window_df = data[(data.index >= start) & (data.index < stop)].copy()

    if window_df.empty:
        start += step_size
        continue

    # Store raw window data for integral before scaling
    raw_window_df = window_df.copy()

    # Normalize
    window_df.loc[:, :] = MinMaxScaler().fit_transform(window_df)

    for pain in pain_variables:
        pain_folder = os.path.join(output_folder, pain)
        os.makedirs(pain_folder, exist_ok=True)

        fig, axs = plt.subplots(nrows=int(np.ceil(len(stressor_vars) / 4)), ncols=4, figsize=(20, 4 * int(np.ceil(len(stressor_vars) / 4))))
        axs = axs.flatten()

        for idx, var in enumerate(stressor_vars):
            if var == pain:
                continue

            lags_list, corrs = cross_correlation(window_df[var], window_df[pain], lags)

            # Compute original (unnormalized) integral
            original_integral = raw_window_df[var].sum()

            axs[idx].plot(lags_list, corrs)
            axs[idx].axvline(0, color='gray', linestyle='--')
            axs[idx].set_title(var)
            axs[idx].set_xlabel("Lag")
            axs[idx].set_ylabel("Correlation")
            axs[idx].grid(True)

            if plot_by_variable_across_time:
                crosscorr_results.append({
                    'pain': pain,
                    'var': var,
                    'start': start,
                    'end': stop,
                    'lags': lags_list,
                    'corrs': corrs,
                    'integral': original_integral
                })

        for j in range(len(stressor_vars), len(axs)):
            fig.delaxes(axs[j])

        fig.suptitle(f"Cross-correlation for {pain} | Window: {start.date()} to {stop.date()}", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fname = os.path.join(pain_folder, f"{pain}_{start.date()}_{stop.date()}.png")
        plt.savefig(fname)
        plt.close(fig)

    # Save intermediate results after each window
    with open(os.path.join(output_folder, "crosscorrelation_data.pkl"), "wb") as f:
        pickle.dump(crosscorr_results, f)

    start += step_size

# --- Optional per-variable plots ---
if plot_by_variable_across_time:
    by_pain_var = {}
    for item in crosscorr_results:
        key = (item['pain'], item['var'])
        by_pain_var.setdefault(key, []).append(item)

    for (pain, var), entries in by_pain_var.items():
        outdir = os.path.join(output_folder, "per_variable", pain)
        os.makedirs(outdir, exist_ok=True)

        if plot_variable_subplots:
            rows = int(np.ceil(np.sqrt(len(entries))))
            cols = int(np.ceil(len(entries) / rows))
            fig, axs = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), sharex=True)
            axs = axs.flatten() if isinstance(axs, np.ndarray) else [axs]
            for i, entry in enumerate(entries):
                label = f"{entry['start'].date()} to {entry['end'].date()}"
                axs[i].plot(entry['lags'], entry['corrs'])
                axs[i].axvline(0, color='gray', linestyle='--')
                axs[i].set_title(label)
                axs[i].set_ylabel("Correlation")
                axs[i].grid(True)
            for ax in axs:
                if ax is not None:
                    ax.set_xlabel("Lag")
            fig.suptitle(f"Cross-correlation of {var} with {pain} across windows")
            fig.tight_layout(rect=[0, 0, 1, 0.95])
            plt.savefig(os.path.join(outdir, f"{pain}_{var}.png"))
            plt.close(fig)
        else:
            plt.figure(figsize=(12, 6))
            for entry in entries:
                label = f"{entry['start'].date()} to {entry['end'].date()}"
                plt.plot(entry['lags'], entry['corrs'], label=label)
            plt.axvline(0, color='gray', linestyle='--')
            plt.title(f"Cross-correlation of {var} with {pain} across windows")
            plt.xlabel("Lag")
            plt.ylabel("Correlation")
            plt.legend(loc='upper right', fontsize='small')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(outdir, f"{pain}_{var}.png"))
            plt.close()
