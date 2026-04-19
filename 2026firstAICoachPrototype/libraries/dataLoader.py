import pandas as pd
import numpy as np

def apply_rolling_minmax(df, columns, window=360):
    """
    Applies rolling min-max scaling to specific columns based on 
    the prior N rows.
    """
    # Create a copy to avoid SettingWithCopy warnings if using a slice
    df = df.copy()
    
    for col in columns:
        # 1. Get the rolling stats shifted by 1 (to only look at priors)
        rolling_min = df[col].shift(1).rolling(window=window).min()
        rolling_max = df[col].shift(1).rolling(window=window).max()
        
        # 2. Calculate the denominator (Max - Min)
        diff = rolling_max - rolling_min
        
        # 3. Scale the column
        # We use .where to avoid division by zero if diff is 0
        df[col] = (df[col] - rolling_min) / diff.replace(0, 1)
        
    return df


def cap_outliers_zscore(df, columns):
    """
    Replaces outliers (beyond 3 standard deviations) with the 
    minimum/maximum values found within the 'normal' range.
    """
    df = df.copy()
    
    for col in columns:
        mean = df[col].mean()
        std = df[col].std()
        
        # 1. Define the 3-sigma thresholds
        lower_threshold = mean - (3 * std)
        upper_threshold = mean + (3 * std)
        
        # 2. Find the min and max of the data that is NOT an outlier
        non_outliers = df[col][(df[col] >= lower_threshold) & (df[col] <= upper_threshold)]
        
        if not non_outliers.empty:
            clean_min = non_outliers.min()
            clean_max = non_outliers.max()
            
            # 3. Replace small outliers with the clean minimum
            df.loc[df[col] < lower_threshold, col] = clean_min
            
            # 4. Replace big outliers with the clean maximum
            df.loc[df[col] > upper_threshold, col] = clean_max
            
    return df


def load_and_preprocess_data(file_path, SPLIT_PERCENT_TrainVal_Test, stressorVarsMinMaxScaler, painRemoveOutliers, SPLIT_PERCENT_Train_Val, printCutOffDates=False):
    
    df = pd.read_pickle(file_path)

    # For the old dataset, map via ferrata days to a fixed climbing effort value
    if 'old' in str(file_path).lower() and 'viaFerrata' in df.columns:
        print("incorporating via ferrata into climbing variable")
        df.loc[df['viaFerrata'] != 0, 'climbingMaxEffortIntensity'] = 5.5

    # Adjusting climbing max effort intensity scale
    veryEasyClimb  = (df['climbingMaxEffortIntensity'] > 0) & (df['climbingMaxEffortIntensity'] < 5.3)
    easyClimb      = (df['climbingMaxEffortIntensity'] >= 5.3) & (df['climbingMaxEffortIntensity'] < 5.8)
    moderateClimb  = (df['climbingMaxEffortIntensity'] >= 5.8) & (df['climbingMaxEffortIntensity'] < 6.0)
    difficultClimb = (df['climbingMaxEffortIntensity'] >= 6.0)
    df.loc[veryEasyClimb, 'climbingMaxEffortIntensity']  = 1
    df.loc[easyClimb, 'climbingMaxEffortIntensity']      = 2
    df.loc[moderateClimb, 'climbingMaxEffortIntensity']  = 3
    df.loc[difficultClimb, 'climbingMaxEffortIntensity'] = 6
    arr2 = df['climbingMaxEffortIntensity'].values
    df['climbingMaxEffortIntensity'] = arr2/np.max(arr2)
    
    # Adjusting climbing denivalation scale
    arr2 = df['climbingDenivelation'].values
    df['climbingDenivelation'] = arr2/np.max(arr2)
    
    stressorCols = [col for col in df.columns.values if not('Pain' in col)]
    painCols     = [col for col in df.columns.values if ('Pain' in col)]
    
    if stressorVarsMinMaxScaler:
      df = apply_rolling_minmax(df, stressorCols, 270)
    
    if painRemoveOutliers:
      df = cap_outliers_zscore(df, painCols)
    
    # Slipping dataset into training and testing sets
    totNbDays = len(df)
    split_TrainVal_Test = int(totNbDays * SPLIT_PERCENT_TrainVal_Test)

    # Selecting the beginning of the dataset for training
    dfTrainAndVal = df.iloc[:split_TrainVal_Test]
    dfTest        = df.iloc[split_TrainVal_Test:]
    
    totNbDays_TrainAndVal = len(dfTrainAndVal)
    split_Train_Val = int(totNbDays_TrainAndVal * SPLIT_PERCENT_Train_Val)
    
    dfTrain = dfTrainAndVal.iloc[:split_Train_Val]
    dfVal   = dfTrainAndVal.iloc[split_Train_Val:]
    
    if printCutOffDates:
      print("dfTrain:", dfTrain.index[0], " to ", dfTrain.index[-1])
      print("dfVal:  ", dfVal.index[0],   " to ", dfVal.index[-1])
      print("dfTest: ", dfTest.index[0],  " to ", dfTest.index[-1])
    
    return [dfTrainAndVal, dfTrain, dfVal, dfTest]
