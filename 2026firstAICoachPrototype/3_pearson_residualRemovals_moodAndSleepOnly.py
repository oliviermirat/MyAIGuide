from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import argparse
from datetime import timedelta
from scipy.stats import pearsonr

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Track specific variables through residual removals.")
parser.add_argument(
    '--only_negative', 
    type=str, 
    default='False', 
    help="Set to True to remove top NEGATIVE correlations instead of positive ones. Defaults to False."
)
args = parser.parse_args()

# --- Parameters ---
only_negative = args.only_negative.lower() in ['true', '1', 'yes', 't']
add_acwr = True          
useNewOrOldData = 'new'  
num_residual_removals = 3

# The variables we explicitly want to track at every stage
tracked_vars = ['generalMood', 'score', 'rhr']

# Derived constant for the loop
total_iterations = num_residual_removals + 1

if useNewOrOldData == 'old':
    startDate = '2016-05-01'
    endDate   = '2021-09-01'
else:
    startDate = '2023-05-15'
    endDate   = '2025-09-11'

# --- Load data ---
if useNewOrOldData == 'new':
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
    
    data = data[pain_variables + ["numberOfSteps", "manicTimeRealTime", "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling", "timeSpentDriving", "timeSpentRidingCar", "phoneTime", "numberOfComputerClicksAndKeyStrokes", "surfCumBpmAbove110", "numberOfHeartBeatsAbove110_upperBodyActivity", "climbingMaxEffortIntensity", "score", "rhr", "generalMood"]]
    
else:
    with open("../../../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb") as f:
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
    lags["ACWR_15_30"] = "acwr_flag" 

def get_shifted_series(data_df, col_name, lag_label, lags_dict):
    if lag_label == "ACWR_15_30":
        acute = pd.concat([data_df[col_name].shift(lag) for lag in range(1, 16)], axis=1).mean(axis=1)
        chronic = pd.concat([data_df[col_name].shift(lag) for lag in range(1, 31)], axis=1).mean(axis=1)
        return acute / chronic.replace(0, np.nan)
    else:
        lag_days = lags_dict[lag_label]
        return pd.concat([data_df[col_name].shift(lag) for lag in lag_days], axis=1).mean(axis=1)

def get_correlations(target_series, target_name, data_df, lags_dict, excluded_cols):
    results = []
    for predictor_col in data_df.columns:
        if predictor_col in excluded_cols:
            continue
            
        for lag_label in lags_dict.keys():
            shifted_predictor = get_shifted_series(data_df, predictor_col, lag_label, lags_dict)
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
                    "P-value": pval,
                    "Significant": (pval < 0.15) or (abs(corr) > 0.10) 
                })
    return pd.DataFrame(results)

print(f"Tracking {tracked_vars} across {num_residual_removals} residual removal stages...")

# Master list to hold all the rows for our final tracked report
tracked_report_data = []

for target_pain in pain_variables:
    if target_pain not in data.columns:
        continue
        
    current_target = data[target_pain].copy()
    
    # Keeps track of what was removed so we can log it contextually
    last_removed_stressor = "Baseline (None)" 
    
    for step in range(total_iterations):
        # 1. Get ALL Correlations (we need all of them to find the top one to remove)
        corr_df = get_correlations(current_target, target_pain, data, lags, pain_variables)
        
        if corr_df.empty:
            break
            
        # --- REPORTING EXTRACT ---
        # Isolate the specific variables we want to track
        step_tracked_df = corr_df[corr_df['Stressor_Variable'].isin(tracked_vars)].copy()
        
        # Add metadata for the report
        step_tracked_df['Iteration'] = step
        step_tracked_df['Context'] = f"After removing: {last_removed_stressor}" if step > 0 else "Baseline"
        
        # Append to master list
        tracked_report_data.append(step_tracked_df)
        
        # --- RESIDUAL REMOVAL LOGIC ---
        # Filter pool based on boolean to find the correct stressor to remove
        if only_negative:
            pool_df = corr_df[(corr_df["Correlation"] < 0) & (corr_df["Significant"] == True)]
            sorted_pool = pool_df.sort_values(by="Correlation", ascending=True) 
        else:
            pool_df = corr_df[(corr_df["Correlation"] > 0) & (corr_df["Significant"] == True)]
            sorted_pool = pool_df.sort_values(by="Correlation", ascending=False)
            
        if step < num_residual_removals and not sorted_pool.empty:
            top_stressor = sorted_pool.iloc[0]["Stressor_Variable"]
            top_lag = sorted_pool.iloc[0]["Lag_Window"]
            last_removed_stressor = f"{top_stressor} ({top_lag})"
            
            x_series = get_shifted_series(data, top_stressor, top_lag, lags)
            x_series = x_series.replace([np.inf, -np.inf], np.nan)
            
            valid_mask = current_target.notna() & x_series.notna()
            X_valid = x_series[valid_mask].values.reshape(-1, 1)
            y_valid = current_target[valid_mask].values
            
            lr = LinearRegression()
            lr.fit(X_valid, y_valid)
            predicted_pain = lr.predict(X_valid)
            
            new_target = current_target.copy()
            new_target.loc[valid_mask] = y_valid - predicted_pain
            current_target = new_target

# --- Save and Print the Master Report ---
if tracked_report_data:
    master_df = pd.concat(tracked_report_data, ignore_index=True)
    
    # Reorder columns for readability
    master_df = master_df[['Pain_Variable', 'Iteration', 'Context', 'Stressor_Variable', 'Lag_Window', 'Correlation', 'P-value']]
    
    # Save FULL report to CSV
    csv_output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "combinedAnalysis",
        "tracked_variables_report.csv"
    )
    master_df.to_csv(csv_output_path, index=False)
    
    # Save SIGNIFICANT ONLY report to CSV
    significant_df = master_df[master_df['P-value'] < 0.05]
    csv_output_path_sig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "combinedAnalysis",
        "tracked_variables_report_significantOnly.csv"
    )
    significant_df.to_csv(csv_output_path_sig, index=False)
    
    # --- PERCENTAGE SUMMARY PER PAIN TYPE AND TRACKED VARIABLE ---
    summary_data = []
    
    # 1. Breakdowns per specific Pain Variable
    for pain in master_df['Pain_Variable'].unique():
        for var in tracked_vars:
            # Filter for specific pain type AND specific tracked variable
            subset_df = significant_df[(significant_df['Pain_Variable'] == pain) & (significant_df['Stressor_Variable'] == var)]
            total_sig = len(subset_df)
            
            if total_sig > 0:
                pos_count = len(subset_df[subset_df['Correlation'] > 0])
                neg_count = len(subset_df[subset_df['Correlation'] < 0])
                
                summary_data.append({
                    "Pain_Variable": pain,
                    "Stressor_Variable": var,
                    "Total_Significant": total_sig,
                    "Positive_Count": pos_count,
                    "Negative_Count": neg_count,
                    "Positive_Percentage": round((pos_count / total_sig) * 100, 2),
                    "Negative_Percentage": round((neg_count / total_sig) * 100, 2)
                })
            else:
                summary_data.append({
                    "Pain_Variable": pain,
                    "Stressor_Variable": var,
                    "Total_Significant": 0,
                    "Positive_Count": 0,
                    "Negative_Count": 0,
                    "Positive_Percentage": 0.0,
                    "Negative_Percentage": 0.0
                })
                
    # 2. Overall Breakdown (Across all pain types)
    for var in tracked_vars:
        # Filter ONLY for the specific tracked variable
        subset_df_overall = significant_df[significant_df['Stressor_Variable'] == var]
        total_sig_overall = len(subset_df_overall)
        
        if total_sig_overall > 0:
            pos_count = len(subset_df_overall[subset_df_overall['Correlation'] > 0])
            neg_count = len(subset_df_overall[subset_df_overall['Correlation'] < 0])
            
            summary_data.append({
                "Pain_Variable": "ALL (Overall)",
                "Stressor_Variable": var,
                "Total_Significant": total_sig_overall,
                "Positive_Count": pos_count,
                "Negative_Count": neg_count,
                "Positive_Percentage": round((pos_count / total_sig_overall) * 100, 2),
                "Negative_Percentage": round((neg_count / total_sig_overall) * 100, 2)
            })
        else:
            summary_data.append({
                "Pain_Variable": "ALL (Overall)",
                "Stressor_Variable": var,
                "Total_Significant": 0,
                "Positive_Count": 0,
                "Negative_Count": 0,
                "Positive_Percentage": 0.0,
                "Negative_Percentage": 0.0
            })
            
    summary_df = pd.DataFrame(summary_data)
    csv_output_path_summary = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "combinedAnalysis",
        "tracked_variables_pos_vs_neg_summary.csv"
    )
    summary_df.to_csv(csv_output_path_summary, index=False)
    
    # Print out nicely to console
    print("\n=========================================================================================")
    print(f"   TRACKED VARIABLES REPORT: {', '.join(tracked_vars)}")
    print("=========================================================================================\n")
    
    for pain_type in master_df['Pain_Variable'].unique():
        print(f">>> TARGET: {pain_type.upper()} <<<")
        pain_subset = master_df[master_df['Pain_Variable'] == pain_type]
        
        for iteration in pain_subset['Iteration'].unique():
            iter_subset = pain_subset[pain_subset['Iteration'] == iteration]
            context = iter_subset['Context'].iloc[0]
            
            print(f"\n--- ITERATION {iteration}: {context} ---")
            print(iter_subset[['Stressor_Variable', 'Lag_Window', 'Correlation', 'P-value']].to_string(index=False))
        print("\n" + "-"*80 + "\n")
        
    print(f"\nSuccessfully saved compiled FULL report to: {csv_output_path}")
    print(f"Successfully saved compiled SIGNIFICANT ONLY report to: {csv_output_path_sig}")
    print(f"Successfully saved POSITIVE VS NEGATIVE SUMMARY to: {csv_output_path_summary}")
else:
    print("No tracking data was generated.")