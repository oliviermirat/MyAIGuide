import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis
import os

def analyze_stressor_distributions(file_path, stressors_list, date_col=None):
    """
    Loads a dataframe, calculates Acute (15d), Chronic (35d), and ACWR variables 
    for specified stressors, and analyzes their distributions for Random Forest suitability.
    """
    print(f"--- Loading data from {file_path} ---")
    
    # 1. Load Data
    if str(file_path).endswith('.csv'):
        df = pd.read_csv(file_path)
    if str(file_path).endswith('.pkl'):
        df = pd.read_pickle(file_path)
    else:
        # Assuming it's already a dataframe for testing purposes
        df = file_path.copy() 

    if date_col and date_col in df.columns:
        df = df.sort_values(by=date_col).reset_index(drop=True)
    
    # 2. Calculate Derived Variables
    print("Calculating Acute (15d), Chronic (35d), and ACWR variables...")
    derived_cols = []
    
    for stressor in stressors_list:
        if stressor not in df.columns:
            print(f"Warning: {stressor} not found in dataframe. Skipping.")
            continue
            
        # Calculate Rolling Averages
        # min_periods=1 ensures we don't get 34 days of NaNs at the start, 
        # but the early ACWR values will be less stable.
        acute_col = f"{stressor}_acute_15d"
        chronic_col = f"{stressor}_chronic_35d"
        acwr_col = f"{stressor}_acwr"
        
        df[acute_col] = df[stressor].rolling(window=15, min_periods=1).mean()
        df[chronic_col] = df[stressor].rolling(window=35, min_periods=1).mean()
        
        # Calculate ACWR (adding a tiny epsilon 1e-9 to avoid division by zero)
        df[acwr_col] = df[acute_col] / (df[chronic_col] + 1e-9)
        
        derived_cols.extend([acute_col, chronic_col, acwr_col])

    # 3. Analyze Distributions
    print("Analyzing distributions...\n")
    results = []
    
    for col in derived_cols:
        data = df[col].dropna()
        if len(data) == 0:
            continue
            
        mean_val = data.mean()
        std_val = data.std()
        
        # Coefficient of Variation (CV) = Std / Mean. Measures relative spread.
        cv = (std_val / mean_val) if mean_val != 0 else np.nan
        
        # Sparsity: proportion of values that are exactly 0
        sparsity = (data == 0).mean()
        
        # Dominance: proportion of the single most frequent value
        most_frequent_prop = data.value_counts(normalize=True).iloc[0]
        
        skewness = skew(data)
        
        # Assessment Logic for Random Forest
        # RF needs variance to split on. If CV is tiny, or one value dominates, it's bad.
        is_enough = True
        warnings = []
        
        if pd.isna(cv) or abs(cv) < 0.01:
            is_enough = False
            warnings.append("Near-zero variance (flatline)")
        if most_frequent_prop > 0.90:
            is_enough = False
            warnings.append(f"Highly dominated by single value ({most_frequent_prop*100:.1f}%)")
        if sparsity > 0.50:
            warnings.append("High sparsity (>50% zeros)")
        if abs(skewness) > 3:
            warnings.append("Highly skewed (heavy outliers)")
            
        status = "✅ Good" if is_enough else "❌ Poor"
        warning_str = " | ".join(warnings) if warnings else "None"
        
        results.append({
            "Variable": col,
            "Type": col.split('_')[-1], # acute, chronic, or acwr
            "RF Suitability": status,
            "CV (Spread)": round(cv, 3) if pd.notna(cv) else "N/A",
            "Skewness": round(skewness, 2),
            "Most Freq Val %": f"{most_frequent_prop*100:.1f}%",
            "Warnings": warning_str
        })

    results_df = pd.DataFrame(results)
    
    # Print Tabular Results
    print(results_df.to_string(index=False))
    print("\n")
    
    # 4. Visualizations
    # Set up the plot grid: rows = number of stressors, cols = 3 (Acute, Chronic, ACWR)
    valid_stressors = [s for s in stressors_list if s in df.columns]
    fig, axes = plt.subplots(len(valid_stressors), 3, figsize=(15, 4 * len(valid_stressors)))
    if len(valid_stressors) == 1:
        axes = [axes] # Handle 1D array indexing for single stressor
    
    sns.set_theme(style="whitegrid")
    
    for i, stressor in enumerate(valid_stressors):
        cols = [f"{stressor}_acute_15d", f"{stressor}_chronic_35d", f"{stressor}_acwr"]
        titles = ["Acute (15d)", "Chronic (35d)", "ACWR"]
        colors = ["#ff9999", "#66b3ff", "#99ff99"]
        
        for j, (col, title, color) in enumerate(zip(cols, titles, colors)):
            ax = axes[i][j]
            data = df[col].dropna()
            
            # Plot Histogram + Kernel Density Estimate
            sns.histplot(data, kde=True, ax=ax, color=color, stat="density", bins=30)
            ax.set_title(f"{stressor} - {title}")
            ax.set_xlabel("Value")
            ax.set_ylabel("Density")
            
    plt.tight_layout()
    plt.show()

    return df, results_df

# =====================================================================
# TEST BLOCK: Run this to see how it works on dummy data!
# =====================================================================
if __name__ == "__main__":
    # 1. Create a dummy dataframe with 100 days of data
    np.random.seed(42)
    days = 100
    dummy_data = pd.DataFrame({
        'day': range(days),
        # Good stressor: Normal daily variations
        'training_load': np.random.normal(loc=500, scale=150, size=days), 
        # Poor stressor: Very little variation, mostly constant
        'sleep_quality': np.random.normal(loc=8, scale=0.1, size=days),
        # Sparse stressor: mostly zeros, occasional spikes
        'match_minutes': np.random.choice([0, 90], size=days, p=[0.8, 0.2])
    })
    
    # 2. Define the list of stressors you want to evaluate
    my_stressors = [
        "numberOfSteps",
        "manicTimeRealTime",
        "timeSpentDriving",
        "cyclingCalories",
        "timeSpentRidingCar",
        "phoneTime",
        "numberOfComputerClicksAndKeyStrokes",
        "surfCumBpmAbove110",
        "numberOfHeartBeatsAbove110_upperBodyActivity",
        "climbingMaxEffortIntensity",
        "score",
        "rhr",
        "generalMood",
    ]
    
    dummy_data = 'newDataset.pkl'
    
    # 3. Run the analysis (Pass the dataframe directly, or pass a "path/to/file.csv")
    processed_df, summary_report = analyze_stressor_distributions(
        file_path=dummy_data, 
        stressors_list=my_stressors
    )