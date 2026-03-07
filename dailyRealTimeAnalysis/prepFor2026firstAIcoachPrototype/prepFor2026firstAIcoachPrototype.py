from calculate_daily_phone_usage import calculate_daily_phone_usage
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import csv
import re

data = pd.read_pickle('dataMay2023andLater.pkl')

new_columns = ['manicTimeRealTime', 'phoneTime']
data[new_columns] = 0

### Getting manicTime data

pathToRealTimeManicTime      = "prepFor2026firstAIcoachPrototype/manicTime.csv"
pathToRealTimeManicTimeBlank = "prepFor2026firstAIcoachPrototype/manicTimeBlank.csv"

with open(pathToRealTimeManicTime, newline="") as csvfile:
  spamreader = csv.reader(csvfile)
  count = 0
  for row in spamreader:
    count = count + 1
    if count > 1 and len(row):
      if row[0][0:4] == "Acti":
        delimit = [m.start() for m in re.finditer("/", row[1])]
        day = row[1][0 : delimit[0]]
        month = row[1][delimit[0] + 1 : delimit[1]]
        if len(month) == 1:
          month = "0" + month
        if len(day) == 1:
          day = "0" + day
        year = row[1][delimit[1] + 1 : delimit[1] + 5]
        date = year + "-" + month + "-" + day
        hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
        if ('2023-05-15' <= date) and (date <= str(data.index[-1])):
          data.loc[date, "manicTimeRealTime"] += hours

  
with open(pathToRealTimeManicTimeBlank, newline="", encoding='utf-8') as csvfile:
  spamreader = csv.reader(csvfile)
  count = 0
  for row in spamreader:
    count = count + 1
    if count > 1 and len(row) and row[0] == "Blank Screen Saver":
      delimit = [m.start() for m in re.finditer("/", row[1])]
      day = row[1][0 : delimit[0]]
      month = row[1][delimit[0] + 1 : delimit[1]]
      if len(month) == 1:
          month = "0" + month
      if len(day) == 1:
          day = "0" + day
      year = row[1][delimit[1] + 1 : delimit[1] + 5]
      date = year + "-" + month + "-" + day
      hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
      if ('2023-05-15' <= date) and (date <= str(data.index[-1])):
        data.loc[date, "manicTimeRealTime"] -= hours
 
# Phone time

daily_usage = calculate_daily_phone_usage("prepFor2026firstAIcoachPrototype/0_phoneTime.csv")

def fill_zeros_with_neighboring_median(df, column_name, window=10):
    """
    Fills 0 values with the median of the preceding N and following N non-zero values.
    """
    # Create a copy to avoid SettingWithCopy warnings
    df_out = df.copy()
    
    # 1. Identify indices and values of non-zero data
    # We use .values for numpy speed
    values = df_out[column_name].values
    non_zero_indices = np.flatnonzero(values != 0)
    non_zero_values = values[non_zero_indices]
    
    # 2. Identify indices that are zero (these are the ones we need to fill)
    zero_indices = np.flatnonzero(values == 0)
    
    # 3. Iterate through zero indices to calculate the specific median
    # We use searchsorted to find where this zero sits relative to non-zeros
    insertion_points = np.searchsorted(non_zero_indices, zero_indices)
    
    filled_values = []
    
    for i, pos in enumerate(insertion_points):
        # Define the window range within the NON-ZERO array
        # We want 'window' items before the insertion point and 'window' items after
        start_idx = max(0, pos - window)
        end_idx = min(len(non_zero_values), pos + window)
        
        # Extract the neighbors
        neighbors = non_zero_values[start_idx:end_idx]
        
        if len(neighbors) > 0:
            filled_values.append(np.median(neighbors))
        else:
            # Fallback if no non-zeros exist in the entire dataframe
            filled_values.append(0)
            
    # 4. Update the dataframe
    # We use specific iloc addressing to update only the zero spots
    df_out.iloc[zero_indices, df.columns.get_loc(column_name)] = filled_values
    
    return df_out

for i in range(len(daily_usage)):
  date  = daily_usage["Date"][i]
  hours = daily_usage["Usage time"][i]
  if ('2023-05-15' <= date) and (date <= str(data.index[-1])):
    data.loc[date, "phoneTime"] = hours

data = fill_zeros_with_neighboring_median(data, 'phoneTime', window=10)


# Sorting

new_order = ['numberOfSteps',
 'timeSpentDriving',
 'timeOnComputer',
 'numberOfComputerClicksAndKeyStrokes',
 'climbingDenivelation',
 'climbingMaxEffortIntensity',
 'swimAndSurfStrokes',
 'scooterRiding',
 'realTimeOtherPain',
 'numberOfHeartBeatsBetween70and110',
 'numberOfHeartBeatsBetween70and110_lowerBodyActivity',
 'numberOfHeartBeatsBetween70and110_upperBodyActivity',
 'numberOfHeartBeatsAbove110',
 'numberOfHeartBeatsAbove110_lowerBodyActivity',
 'numberOfHeartBeatsAbove110_upperBodyActivity',
 'cyclingCalories',
 'timeSpentRidingCar',
 'timeInCar',
 'computerAndCarTime',
 'garminClimbingActiveCalories',
 'garminKneeRelatedActiveCalories',
 'numberOfHeartBeatsBetween70and110_lowerBodyActivity_cycling',
 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling',
 'realTimeSick',
 'garminCliffJumpingActiveCalories',
 'score',
 'rhr',
 'kneePain',
 'armPain',
 'facePain',
 'manicTimeRealTime',
 'phoneTime',
 'surfing',
 'swimming']

data = data[new_order]

###

data = data[data.index >= '2023-05-15']
data = data[data.index <= '2025-09-11']

###

data['surfing2']  = data['surfing'].copy()
data['swimming2'] = data['swimming'].copy()

both_mask = (data['surfing'] == 1) & (data['swimming'] == 1)
surf_only_mask = (data['surfing'] == 1) & (data['swimming'] != 1)
swim_only_mask = (data['swimming'] == 1) & (data['surfing'] != 1)

data.loc[both_mask, 'surfing'] = data.loc[both_mask, 'swimAndSurfStrokes'] / 2
data.loc[both_mask, 'swimming'] = data.loc[both_mask, 'swimAndSurfStrokes'] / 2
data.loc[surf_only_mask, 'surfing'] = data.loc[surf_only_mask, 'swimAndSurfStrokes']
data.loc[swim_only_mask, 'swimming'] = data.loc[swim_only_mask, 'swimAndSurfStrokes']

data.rename(columns={'surfing': 'surfStrokes', 'swimming': 'swimStrokes'}, inplace=True)

data.loc[both_mask, 'surfing2'] = data.loc[both_mask, 'numberOfHeartBeatsAbove110_upperBodyActivity'] / 2
data.loc[both_mask, 'swimming2'] = data.loc[both_mask, 'numberOfHeartBeatsAbove110_upperBodyActivity'] / 2
data.loc[surf_only_mask, 'surfing2'] = data.loc[surf_only_mask, 'numberOfHeartBeatsAbove110_upperBodyActivity']
data.loc[swim_only_mask, 'swimming2'] = data.loc[swim_only_mask, 'numberOfHeartBeatsAbove110_upperBodyActivity']

data.rename(columns={'surfing2': 'surfCumBpmAbove110', 'swimming2': 'swimCumBpmAbove110'}, inplace=True)

###

data.to_pickle('dataMay2023andLater_2026firstAIPrototype.pkl')
