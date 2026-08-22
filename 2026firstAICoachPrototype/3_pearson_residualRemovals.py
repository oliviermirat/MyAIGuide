from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import json
import argparse
from datetime import timedelta
from scipy.stats import pearsonr

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Find Candidate Stressors using Pearson Correlation.")
parser.add_argument(
    '--only_negative', 
    type=str, 
    default='False', 
    help="Set to True to ONLY look for negative correlations. Defaults to False."
)
parser.add_argument(
    '--save_excel', 
    type=str, 
    default='False', 
    help="Set to True to save intermediate Excel files for each step. Defaults to False."
)
args = parser.parse_args()

# --- Parameters ---
only_negative = args.only_negative.lower() in ['true', '1', 'yes', 't']
save_excel = args.save_excel.lower() in ['true', '1', 'yes', 't'] # Controls saving of .xlsx files
add_acwr = True          # When True, adds Acute:Chronic Workload Ratio (15/30 days) to lag windows
add_cyclingCalories = False
useNewOrOldData = 'new'  # 'new' or 'old'
num_residual_removals = 3
nbToPrint = 1

# Derived constant for the loop
total_iterations = num_residual_removals + 1

if useNewOrOldData == 'old':
    startDate = '2016-05-01'
    endDate   = '2021-09-01'
else:
    startDate = '2023-05-15'
    endDate   = '2025-09-11'

# --- File Logging Setup ---
txt_output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "results", "combinedAnalysis",
    "candidateStressorsPearson_console_output_negativesOnly.txt" if only_negative else "candidateStressorsPearson_console_output_positivesOnly.txt"
)
txt_file = open(txt_output_path, "w", encoding="utf-8")

def log_print(msg=""):
    """Helper to print to console and write to the text file simultaneously."""
    print(msg)
    txt_file.write(str(msg) + "\n")
    
# --- Load data ---
if useNewOrOldData == 'new':
    # Ensure this path is correct on your laptop
    with open("./dataMay2023andLater_2026firstAIPrototype.pkl", "rb") as f:  
        data = pickle.load(f)
        
    # Manual data injection
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
    
    if add_cyclingCalories:
        data = data[pain_variables + ["numberOfSteps", "manicTimeRealTime", "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling", "timeSpentDriving", "timeSpentRidingCar", "phoneTime", "numberOfComputerClicksAndKeyStrokes", "surfCumBpmAbove110", "numberOfHeartBeatsAbove110_upperBodyActivity", "climbingMaxEffortIntensity", "score", "generalMood", "cyclingCalories"]] #"rhr"
    else:
        data = data[pain_variables + ["numberOfSteps", "manicTimeRealTime", "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling", "timeSpentDriving", "timeSpentRidingCar", "phoneTime", "numberOfComputerClicksAndKeyStrokes", "surfCumBpmAbove110", "numberOfHeartBeatsAbove110_upperBodyActivity", "climbingMaxEffortIntensity", "score", "generalMood"]] #"rhr"

else:
    with open("./oldDataset.txt", "rb") as f:
        data = pickle.load(f)
    
    data = data.drop(columns=[
        'sick_tired', 'painInOtherRegion', 'foreheadPain', 'eyesPain',
        'shoulderPain', 'elbowPain', 'generalmood', 'handsAndFingerPain',
        'forearmElbowPain', 'shoulderNeckPain', 'foreheadAndEyesPain',
        'aroundEyesPain', 'fingerHandArmPain', 'fingersPain'])
    
    pain_variables = ['kneePain', 'foreheadEyesPain', 'wholeArm']

# --- Filter and smooth data ---
data = data[(data.index >= startDate) & (data.index <= endDate)]
data.index = pd.to_datetime(data.index)

# --- Correlation Analysis ---
lags = {
    "same_day": [0],
    "previous_day": [1],
    "previous_2_days": [1, 2],
    "previous_4_days": [1, 2, 3, 4],
    "previous_15_days": [i for i in range(1, 16)],
    "previous_30_days": [i for i in range(1, 31)], 
    "previous_45_days": [i for i in range(1, 46)], 
    "previous_60_days": [i for i in range(1, 61)], 
}

if add_acwr:
    lags["ACWR_15_30"] = "acwr_flag" # Added dynamically based on the boolean

def get_shifted_series(data_df, col_name, lag_label, lags_dict):
    """Helper to generate the shifted series, dynamically handling standard lags and ACWR."""
    if lag_label == "ACWR_15_30":
        acute = pd.concat([data_df[col_name].shift(lag) for lag in range(1, 16)], axis=1).mean(axis=1)
        chronic = pd.concat([data_df[col_name].shift(lag) for lag in range(1, 31)], axis=1).mean(axis=1)
        # Avoid division by zero by replacing 0s in chronic with NaN
        return acute / chronic.replace(0, np.nan)
    else:
        lag_days = lags_dict[lag_label]
        return pd.concat([data_df[col_name].shift(lag) for lag in lag_days], axis=1).mean(axis=1)

def rolling_mean_days(lag_label):
    """Number of days in the rolling mean window for a given lag label."""
    if lag_label == "ACWR_15_30":
        return 30 # ACWR requires 30 days of data to compute
    return len(lags[lag_label])

def get_correlations(target_series, target_name, data_df, lags_dict, excluded_cols):
    """Helper function to run correlations against a dynamic target series (raw pain or residuals)"""
    results = []
    for predictor_col in data_df.columns:
        if predictor_col in excluded_cols:
            continue
            
        for lag_label in lags_dict.keys():
            # Utilize the new helper function for generating predictors
            shifted_predictor = get_shifted_series(data_df, predictor_col, lag_label, lags_dict)
            
            # Clean up potential infinities if data anomalies occurred
            shifted_predictor = shifted_predictor.replace([np.inf, -np.inf], np.nan)

            valid_mask = target_series.notna() & shifted_predictor.notna()
            y_target = target_series[valid_mask]       
            x_stressor = shifted_predictor[valid_mask] 

            if len(y_target) > 5:
                corr, pval = pearsonr(x_stressor, y_target)
                results.append({
                    "Pain_Variable": target_name,
                    "Stressor_Variable": predictor_col,
                    "Lag_Window": lag_label,
                    "Correlation": corr,
                    "Abs_Correlation": abs(corr), 
                    "P-value": pval,
                    # Implemented 'Loose Gate' to avoid deleting interacting variables
                    "Significant": (pval < 0.15) or (abs(corr) > 0.10) 
                })
    return pd.DataFrame(results)

def build_step_correlations_json(corr_df, max_features=10, pvalue_threshold=0.05, is_negative=False):
    """Top correlations with p-value below threshold for JSON export."""
    if corr_df is None or corr_df.empty:
        return []

    if is_negative:
        filtered = corr_df[
            (corr_df["Correlation"] < 0) & (corr_df["P-value"] < pvalue_threshold)
        ].sort_values(by="Correlation", ascending=True).head(max_features)
    else:
        filtered = corr_df[
            (corr_df["Correlation"] > 0) & (corr_df["P-value"] < pvalue_threshold)
        ].sort_values(by="Correlation", ascending=False).head(max_features)

    return [
        {
            "feature": row["Stressor_Variable"],
            "lag_window": row["Lag_Window"],
            "rolling_mean_days": rolling_mean_days(row["Lag_Window"]),
            "correlation": float(row["Correlation"]),
            "p_value": float(row["P-value"]),
        }
        for _, row in filtered.iterrows()
    ]

log_print(f"Analyzing {len(data.columns)} variables with {num_residual_removals} stages of residual extraction...")

# Dictionary to store the results dynamically based on total_iterations
final_printout_data = {pain: {i: None for i in range(total_iterations)} for pain in pain_variables}
# Keep track of which stressors were removed for clarity
removed_stressors_log = {pain: [] for pain in pain_variables}
removed_stressors_rolling_days_log = {pain: [] for pain in pain_variables}

for target_pain in pain_variables:
    if target_pain not in data.columns:
        continue
        
    # Initialize the target variable (Starts as raw pain, becomes residuals)
    current_target = data[target_pain].copy()
    
    for step in range(total_iterations):
        # 1. Get Correlations
        corr_df = get_correlations(current_target, target_pain, data, lags, pain_variables)
        
        # --- Filter based on the boolean ---
        if only_negative:
            corr_df = corr_df[corr_df["Correlation"] < 0]
        else:
            corr_df = corr_df[corr_df["Correlation"] > 0]
        
        # Save Excel files if enabled
        if save_excel:
            corr_df.to_excel(target_pain + "_" + str(step) + ".xlsx")
        
        if corr_df.empty:
            break
            
        # Filter and Sort (Sorting changes based on negative vs positive search)
        signif_df = corr_df[corr_df["Significant"] == True]
        if only_negative:
            sorted_df = signif_df.sort_values(by="Correlation", ascending=True) # Lowest negative at the top
        else:
            sorted_df = signif_df.sort_values(by="Correlation", ascending=False) # Highest positive at the top
            
        final_printout_data[target_pain][step] = sorted_df
        
        # 2. Extract Residuals (For all steps except the final printout step)
        if step < num_residual_removals and not sorted_df.empty:
            target_corrs = sorted_df.copy()
            
            if target_corrs.empty:
                removed_stressors_log[target_pain].append("None (No matching correlations left)")
                break
                
            top_stressor = target_corrs.iloc[0]["Stressor_Variable"]
            top_lag = target_corrs.iloc[0]["Lag_Window"]
            removed_stressors_log[target_pain].append(f"{top_stressor} ({top_lag})")
            removed_stressors_rolling_days_log[target_pain].append(rolling_mean_days(top_lag))
            
            # Re-create the exact stressor data using the helper to account for ACWR
            x_series = get_shifted_series(data, top_stressor, top_lag, lags)
            x_series = x_series.replace([np.inf, -np.inf], np.nan)
            
            # Align non-NaN data for regression
            valid_mask = current_target.notna() & x_series.notna()
            X_valid = x_series[valid_mask].values.reshape(-1, 1)
            y_valid = current_target[valid_mask].values
            
            # Fit Linear Regression and predict
            lr = LinearRegression()
            lr.fit(X_valid, y_valid)
            predicted_pain = lr.predict(X_valid)
            
            # Calculate Residuals (Actual - Predicted) and update the target for the next loop
            new_target = current_target.copy()
            new_target.loc[valid_mask] = y_valid - predicted_pain
            current_target = new_target

# --- Build JSON output ---
pearson_results_json = {}

for pain_type in pain_variables:
    if final_printout_data[pain_type][0] is None:
        continue

    pain_steps = {}
    for step in range(total_iterations):
        df_step = final_printout_data[pain_type].get(step)
        if df_step is None:
            break

        # Dynamically set JSON key
        json_key = "top_negative_correlations" if only_negative else "top_positive_correlations"
        
        step_entry = {
            json_key: build_step_correlations_json(df_step, is_negative=only_negative),
        }

        if step < len(removed_stressors_rolling_days_log[pain_type]):
            step_entry["residual_removal_rolling_mean_days"] = (
                removed_stressors_rolling_days_log[pain_type][step]
            )

        if step == 0:
            step_entry["description"] = "baseline_before_first_residual_removal"
        else:
            removed_name = (
                removed_stressors_log[pain_type][step - 1]
                if len(removed_stressors_log[pain_type]) > step - 1
                else "None"
            )
            step_entry["description"] = f"after_removing_{removed_name}"

        pain_steps[f"step_{step}"] = step_entry

    pearson_results_json[pain_type] = pain_steps

json_output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "results", "combinedAnalysis",
    "candidateStressorsPearson_console_output_negativesOnly.json" if only_negative else "candidateStressorsPearson_console_output_positivesOnly.json",
)
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(pearson_results_json, f, indent=2)

log_print(f"\nSaved Pearson correlation results to {json_output_path}")

# --- Process & Print Results ---
correlation_type_str = "NEGATIVE" if only_negative else "POSITIVE"
log_print("\n==================================================")
log_print(f"       TOP {correlation_type_str} CORRELATIONS PER PAIN TYPE")
log_print("==================================================")

for pain_type in pain_variables:
    if final_printout_data[pain_type][0] is None:
        continue
        
    log_print(f"\n\n>>> TARGET: {pain_type.upper()} <<<")
    
    # Dynamically print out each iteration block
    for step in range(total_iterations):
        df_step = final_printout_data[pain_type].get(step)
        
        if df_step is None:
            break
            
        if step == 0:
            log_print(f"\n--- ITERATION {step}: Baseline (Before any removal) ---")
        else:
            # Retrieve the name of the stressor that was removed in the previous step
            removed_name = removed_stressors_log[pain_type][step-1] if len(removed_stressors_log[pain_type]) > step-1 else "None"
            log_print(f"\n--- ITERATION {step}: After removing effect of [{removed_name}] ---")
            
        if not df_step.empty:
            log_print(df_step[['Stressor_Variable', 'Lag_Window', 'Correlation', 'P-value']].head(nbToPrint).to_string(index=False))
        else:
            log_print(f"No significant {correlation_type_str.lower()} triggers found for Iteration {step}.")

log_print("\nAnalysis Complete.")

# Close the output text file
txt_file.close()
print(f"Console output successfully saved to {txt_output_path}") # This line uses standard print() because the log file is now closed

###

# --- Generate Publication-Ready Excel Summary ---

# --- Generate Publication-Ready Excel & HTML Summary ---

# Map raw dataset variables to presentation-friendly names
pretty_names_map = {
    "manicTimeRealTime": "Time spent on computer",
    "score": "Sleep score",
    "numberOfComputerClicksAndKeyStrokes": "Number of keyboard and mouse clicks",
    "numberOfSteps": "Number of steps taken",
    "timeSpentDriving": "Time spent driving a car",
    "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling": "Cycling cumulative bpm > 110",
    "generalMood": "General mood",
    "numberOfHeartBeatsAbove110_upperBodyActivity": "Upper-body cumulative bpm > 110",
    "hrv": "Heart rate variability",
    "surfCumBpmAbove110": "Surf cumulative bpm > 110",
    "climbingMaxEffortIntensity": "Rock climbing maximum route grade",
    "timeSpentRidingCar": "Time spent riding in a vehicle",
    "phoneTime": "Time spent using a mobile phone",
    "movingBadSuitcase": "Moving bad suitcase" 
}

def format_publication_cell(step_data):
    """Extracts top stressor and formats temporal window/correlation/p-value for publication."""
    if step_data is None or step_data.empty:
        return "-"
    
    # Grab the top correlated stressor for this specific step
    top_row = step_data.iloc[0]
    raw_stressor = top_row["Stressor_Variable"]
    corr = top_row["Correlation"]
    pval = top_row["P-value"]
    lag_label = top_row["Lag_Window"]
    
    # Swap raw name for pretty name (defaults to raw name if not found in dictionary)
    pretty_stressor = pretty_names_map.get(raw_stressor, raw_stressor)
    
    # Format the temporal window (handle ACWR vs standard rolling mean)
    if lag_label == "ACWR_15_30":
        temporal_window = "15/30-day ACWR"
    else:
        days = rolling_mean_days(lag_label)
        day_str = "day" if days == 1 else "days"
        temporal_window = f"{days} {day_str}"
    
    # Format p-value to APA publication style
    if pval < 0.001:
        pval_str = "p < .001"
    else:
        # Removes the leading zero for p-values (e.g., p = .045)
        pval_str = f"p = {pval:.3f}".replace("0.", ".")
        
    # Combines the stressor name, temporal window, and stats in one cell
    return f"{pretty_stressor} ({temporal_window}, r = {corr:.2f}, {pval_str})"


# Dynamically map the pain variables based on 'old' or 'new' dataset naming
region_mapping = {
    "face": next((p for p in pain_variables if "face" in p.lower() or "forehead" in p.lower()), None),
    "knee": next((p for p in pain_variables if "knee" in p.lower()), None),
    "arm": next((p for p in pain_variables if "arm" in p.lower()), None)
}

summary_rows = []

# Loop through 3 lines (Step 0: pre-residual, Step 1: 1st removal, Step 2: 2nd removal)
for step in range(3): 
    if step == 0:
        step_name = "Pre-residual"
    else:
        step_name = f"Residual removal step {step}"
        
    row_data = {"Step": step_name}
    
    # Iterate in the exact column order requested: face, knee, arm
    for region in ["face", "knee", "arm"]:
        pain_var = region_mapping[region]
        if pain_var and final_printout_data.get(pain_var):
            df_step = final_printout_data[pain_var].get(step)
            row_data[region] = format_publication_cell(df_step)
        else:
            row_data[region] = "-"
            
    summary_rows.append(row_data)

summary_df = pd.DataFrame(summary_rows)

# Enforce the column order
summary_df = summary_df[["Step", "face", "knee", "arm"]]

# Save to Excel
output_excel_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "results", "combinedAnalysis",
    "publication_summary_correlations.xlsx"
)
summary_df.to_excel(output_excel_path, index=False)

# Make sure you're printing to the console and not the closed txt_file
print(f"Publication-ready Excel file successfully saved to: {output_excel_path}")