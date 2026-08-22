import pandas as pd
import numpy as np
import pickle
import os
from sklearn.metrics import roc_curve

# --- Parameters ---
window = 7
baseline_days = 45 # Using your preferred 45-day baseline
flare_percentile = 0.75 #0.75 # Top 25% of pain increases are considered a "Flare"
useNewOrOldData = 'new'

if useNewOrOldData == 'old':
    startDate = '2016-05-01'
    endDate   = '2021-09-01'
else:
    startDate = '2023-05-15'
    endDate   = '2025-09-11'

# The two trusted pairs
trusted_pairs = [
    {'pain': 'armPain', 'stressor': 'surfCumBpmAbove110'},
    {'pain': 'kneePain', 'stressor': 'numberOfSteps'},
    {'pain': 'kneePain', 'stressor': 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling'}
]

# --- Load data ---
print("Loading data...")
if useNewOrOldData == 'new':
    with open("./dataMay2023andLater_2026firstAIPrototype.pkl", "rb") as f:  
        data = pickle.load(f)
else:
    with open("../../../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb") as f:
        data = pickle.load(f)

data = data[(data.index >= startDate) & (data.index <= endDate)]
data.index = pd.to_datetime(data.index)

print(f"\n==================================================")
print(f"       JAGGEDNESS THRESHOLD ANALYSIS")
print(f"==================================================")

for pair in trusted_pairs:
    target_pain = pair['pain']
    stressor = pair['stressor']
    
    if target_pain not in data.columns or stressor not in data.columns:
        continue
        
    print(f"\n>>> Analyzing: {stressor} -> {target_pain.upper()} <<<")
    
    # 1. Compute Continuous Delta Pain
    baseline_pain = data[target_pain].shift(1).rolling(window=baseline_days, min_periods=2).mean()
    delta_pain = data[target_pain] #- baseline_pain
    
    # 2. Calculate Volume and Variation (SHIFTED by 1 day)
    rolling_volume = data[stressor].rolling(window=window).sum().shift(1)
    daily_diff = data[stressor].diff().abs()
    rolling_variation = daily_diff.rolling(window=window).sum().shift(1)
    
    # 3. Calculate Jaggedness Index
    jaggedness = rolling_variation / rolling_volume.replace(0, np.nan)
    
    # 4. Assemble Data
    temp_df = pd.DataFrame({
        'volume': rolling_volume,
        'jaggedness': jaggedness,
        'delta_pain': delta_pain
    }).dropna()
    
    # Filter out 7-day windows with absolute zero activity
    temp_df = temp_df[temp_df['volume'] > 0]
    
    if len(temp_df) < 50: 
        print("Not enough data points.")
        continue
        
    # 5. Define a "Flare" (Target Variable)
    # E.g., The threshold for the top 25% of pain increases
    flare_threshold = temp_df['delta_pain'].quantile(flare_percentile)
    temp_df['is_flare'] = (temp_df['delta_pain'] > flare_threshold).astype(int)
    
    # 6. Risk Gradient (Quintiles)
    try:
        temp_df['jaggedness_tier'] = pd.qcut(temp_df['jaggedness'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'], duplicates='drop')
        
        print(f"\n--- Flare Risk by Jaggedness Tier ---")
        summary = temp_df.groupby('jaggedness_tier', observed=False).agg(
            Avg_Volume=('volume', 'mean'),          # <--- Added Volume Aggregation
            Avg_Jaggedness=('jaggedness', 'mean'),
            Flare_Probability=('is_flare', 'mean'),
            Days_in_Tier=('is_flare', 'count')
        )
        for index, row in summary.iterrows():
            # Added Avg Vol to the printout string
            print(f"Tier: {index:<10} | Avg Vol: {row['Avg_Volume']:>8.1f} | Avg Jaggedness: {row['Avg_Jaggedness']:.3f} | Flare Risk: {row['Flare_Probability']*100:.1f}%")
            
    except ValueError:
        print("Could not calculate quintiles (data too heavily clustered).")

    # 7. Optimal Threshold (Youden's J Statistic)
    fpr, tpr, thresholds = roc_curve(temp_df['is_flare'], temp_df['jaggedness'])
    
    # Youden's J = Sensitivity (tpr) + Specificity (1 - fpr) - 1
    # We want to maximize this to find the best cut-point
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]
    
    print(f"\n--- Optimal 'Danger' Threshold ---")
    print(f"If Jaggedness exceeds: {optimal_threshold:.3f}, the risk of a flare jumps significantly.")
    print(f"(This threshold maximizes true positives while minimizing false alarms.)\n")

print("Analysis Complete.")