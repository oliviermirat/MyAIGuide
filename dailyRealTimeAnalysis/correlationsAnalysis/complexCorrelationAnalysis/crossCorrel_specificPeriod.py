from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

plotTimeSeries = True
rolling_window = 7
max_lag = 50
useNewOrOldData = 'new' #'old' # 'new'
predictorToTest = 'numberOfSteps' #'numberOfHeartBeatsAbove110_lowerBodyActivity' #numberOfHeartBeatsAbove110_upperBodyActivity' #'garminClimbingActiveCalories' #'swimAndSurfStrokes' #'tracker_mean_distance' # 'numberOfSteps'
painToTest      = 'armPain'
startDate = '2024-05-15' # '2016-08-15'
endDate = '2024-11-15' # '2018-01-01'

# Load the data (adjust path if needed)
if useNewOrOldData == 'new':
    with open("dataMay2023andLater.pkl", "rb") as f:
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
elif useNewOrOldData == 'old':
    inputt = open("../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb")
    data = pickle.load(inputt)
    inputt.close()
    # Removing some variables
    data = data.drop(columns=[
        'sick_tired',
        'painInOtherRegion',
        'foreheadPain',
        'eyesPain',
        'shoulderPain',
        'elbowPain',
        'generalmood',
        'handsAndFingerPain',
        'forearmElbowPain',
        'shoulderNeckPain',
        'foreheadAndEyesPain', 
        'aroundEyesPain',
        'fingerHandArmPain', 
        'fingersPain', 
        # 'wholeArm'
    ])


print(data.columns)


data = data[data.index >= startDate]
data = data[data.index <= endDate]


# Extract and preprocess the relevant variables
df = data[[predictorToTest, painToTest]].dropna()
df = df.rolling(rolling_window).mean().dropna()

# Normalize the variables (z-score standardization) or use MinMaxScaler
if False:
  df[predictorToTest] = (df[predictorToTest] - df[predictorToTest].mean()) / df[predictorToTest].std()
  df[painToTest] = (df[painToTest] - df[painToTest].mean()) / df[painToTest].std()
else:
  df.loc[:, :] = MinMaxScaler().fit_transform(df)

if plotTimeSeries:
  df.plot()
  plt.show()

# Cross-correlation function
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

# Compute cross-correlation
lags = list(range(-max_lag, max_lag + 1))
lags, corrs = cross_correlation(df[predictorToTest], df[painToTest], lags)

# Identify best lag and correlation
best_idx = np.nanargmax(corrs)
best_lag = lags[best_idx]
max_corr = corrs[best_idx]

print(f"\n📊 Best lag: {best_lag}")
print(f"📈 Max correlation: {max_corr:.3f}")
if best_lag > 0:
    print(f"→ " + predictorToTest + " may be causing " + painToTest + " (lead of {best_lag} days)")
elif best_lag < 0:
    print(f"→ " + painToTest + " may be causing " + predictorToTest + " (lag of {-best_lag} days)")
else:
    print("→ " + predictorToTest + " and " + painToTest + " move synchronously (lag = 0)")

# Plot cross-correlation
plt.figure(figsize=(10, 5))
plt.plot(lags, corrs, marker='o')
plt.axvline(x=0, color='gray', linestyle='--')
plt.axvline(x=best_lag, color='red', linestyle='--', label=f'Max Corr Lag ({best_lag})')
plt.title("Cross-correlation: " + predictorToTest + " → " + painToTest + "")
plt.xlabel("Lag (" + predictorToTest + " shifted)")
plt.ylabel("Correlation coefficient")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
