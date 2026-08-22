import pandas as pd
import numpy as np
import pickle
import os
import argparse
from scipy.stats import pearsonr

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Continuous Irregularity via Shifted Jaggedness Index (Direct Correlation).")
parser.add_argument('--window_days', type=int, default=7, help="Rolling window to calculate Volume and Jaggedness.")
parser.add_argument('--baseline_days', type=int, default=45, help="Days for rolling baseline to compute Delta Pain.")
args = parser.parse_args()

# --- Parameters ---
window = args.window_days
baseline_days = args.baseline_days
useNewOrOldData = 'new'

if useNewOrOldData == 'old':
    startDate = '2016-05-01'
    endDate   = '2021-09-01'
else:
    startDate = '2023-05-15'
    endDate   = '2025-09-11'

# --- File Logging Setup ---
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "regularityAnalysis")
os.makedirs(output_dir, exist_ok=True)
txt_output_path = os.path.join(output_dir, "continuous_jaggedness_direct.txt")
txt_file = open(txt_output_path, "w", encoding="utf-8")

def log_print(msg=""):
    print(msg)
    txt_file.write(str(msg) + "\n")

# --- Load data ---
log_print("Loading data...")
if useNewOrOldData == 'new':
    with open("./dataMay2023andLater_2026firstAIPrototype.pkl", "rb") as f:  
        data = pickle.load(f)
        
    pain_variables = ['kneePain', 'armPain', 'facePain']
    stressors = [
        "numberOfSteps", "manicTimeRealTime", "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling", 
        "timeSpentDriving", "timeSpentRidingCar", "phoneTime", "numberOfComputerClicksAndKeyStrokes", 
        "surfCumBpmAbove110", "numberOfHeartBeatsAbove110_upperBodyActivity", "climbingMaxEffortIntensity"
    ]
    data = data[pain_variables + stressors]
else:
    with open("../../../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb") as f:
        data = pickle.load(f)
    pain_variables = ['kneePain', 'foreheadEyesPain', 'wholeArm']
    stressors = [col for col in data.columns if col not in pain_variables]

data = data[(data.index >= startDate) & (data.index <= endDate)]
data.index = pd.to_datetime(data.index)

# --- Analysis Logic ---
log_print(f"\nEvaluating Continuous Irregularity via 'Jaggedness Index'.")
log_print(f"Target: Delta Pain (Today - Prior {baseline_days}-day avg).")
log_print(f"Predictors: Shifted by 1 day to prevent reverse-causation (resting due to pain).")
log_print(f"Method: Direct Pearson Correlation of Jaggedness vs Delta Pain.\n")

results_list = []

for target_pain in pain_variables:
    if target_pain not in data.columns:
        continue
        
    log_print(f"==================================================")
    log_print(f">>> TARGET PAIN: {target_pain.upper()} <<<")
    log_print(f"==================================================")
    
    # 1. Compute Continuous Delta Pain (Acute Flare)
    # This evaluates today's pain relative to the previous baseline
    baseline_pain = data[target_pain].shift(1).rolling(window=baseline_days, min_periods=2).mean()
    delta_pain = data[target_pain] #- baseline_pain
    
    for stressor in stressors:
        if stressor not in data.columns:
            continue
            
        # 2. Calculate Volume and Variation (SHIFTED by 1 day)
        # This ensures we only look at the 7 days leading *up to* the pain
        rolling_volume = data[stressor].rolling(window=window).sum().shift(1)
        
        # Absolute day-to-day difference in load
        daily_diff = data[stressor].diff().abs()
        # Sum of those differences over the window, also shifted
        rolling_variation = daily_diff.rolling(window=window).sum().shift(1)
        
        # 3. Calculate Jaggedness Index
        jaggedness = rolling_variation / rolling_volume.replace(0, np.nan)
        
        # 4. Assemble and align data
        temp_df = pd.DataFrame({
            'rolling_volume': rolling_volume,
            'jaggedness': jaggedness,
            'delta_pain': delta_pain
        }).dropna()
        
        # Filter out 7-day windows with absolute zero activity
        temp_df = temp_df[temp_df['rolling_volume'] > 0]
        
        if len(temp_df) < 20: 
            continue

        # 5. Direct Correlations
        corr_vol, p_val_vol = pearsonr(temp_df['rolling_volume'], temp_df['delta_pain'])
        corr_jag, p_val_jag = pearsonr(temp_df['jaggedness'], temp_df['delta_pain'])
        
        results_list.append({
            'Pain_Variable': target_pain,
            'Stressor': stressor,
            'N_Active_Windows': len(temp_df),
            'Mean_Volume': temp_df['rolling_volume'].mean(),
            'Mean_Jaggedness': temp_df['jaggedness'].mean(),
            'Correlation_Volume_vs_DeltaPain': corr_vol,
            'P_Value_Volume': p_val_vol,
            'Correlation_Jaggedness_vs_DeltaPain': corr_jag,
            'P_Value_Jaggedness': p_val_jag,
            'Significant_Jaggedness': p_val_jag < 0.05
        })
        
        if p_val_jag < 0.05:
            log_print(f"[!] Significant Jaggedness Correlation: {stressor}")
            log_print(f"    Volume vs Delta Pain: r = {corr_vol:.3f} (p = {p_val_vol:.4f})")
            log_print(f"    Jaggedness vs Delta Pain: r = {corr_jag:.3f} (p = {p_val_jag:.4f}) | (N={len(temp_df)})\n")

    log_print("\n")

# --- Save Results to Excel ---
results_df = pd.DataFrame(results_list)

if not results_df.empty:
    results_df = results_df.sort_values(
        by=['Pain_Variable', 'Significant_Jaggedness', 'Correlation_Jaggedness_vs_DeltaPain', 'P_Value_Jaggedness'],
        ascending=[True, False, False, True]
    )
    
    excel_path = os.path.join(output_dir, "continuous_jaggedness_direct.xlsx")
    results_df.to_excel(excel_path, index=False)
    log_print(f"Full tabular results logically ranked and saved to: {excel_path}")
else:
    log_print("No sufficient data variations found to output Excel summary.")

log_print("Analysis Complete.")
txt_file.close()