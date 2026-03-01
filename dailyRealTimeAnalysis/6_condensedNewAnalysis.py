from sklearn.preprocessing import MinMaxScaler
import sqlite3
import pandas as pd
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pyexcel_ods
import csv
import os
import re
import sys
sys.path.insert(1, '../src/MyAIGuide/dataFromGarmin')
from garminDataGatheredFromWebExport import garminDataGatheredFromWebExport, garminActivityDataGatheredFromWebExport
import json
import numpy as np
import condensedAnalysisFunctions


##### Parameters

extendedDataSaving = True

heart_rate_active_threshold_values = [70, 110]

saveFigs = False
figWidth  = 20
figHeight = 5.1
hspace   = 0.4
lineWidth = 1

figsFormat = 'png'

rollingWindow = 14

replaceCyclingCaloriesByGarminCyclingHr = True

if replaceCyclingCaloriesByGarminCyclingHr:
  additionalActivities = ['cycling']
else:
  additionalActivities = []

cutoff_date = "2023-05-15"

keyToCoeff1 = {'walking':           'walking',
               'cycling':           'cycling',
               'swimming':          'swimming',
               'surfing':           'swimming',
               'rock_climbing':     'rock_climbing',
               'generic':           'rock_climbing', 
               'training':          'homeExercises',
               'fitness_equipment': 'homeExercises',
               'Cliff jumping':     '50/50',
               'Cliff jumping ':    '50/50',
               'Gardening':         '50/50',
               'Handyman work':     'homeExercises',
               'House Cleaning':    '50/50',
               'House cleaning':    '50/50',
               'Other':             'rock_climbing',
               'Sawing':            'homeExercises',
               'Trail building':    '50/50',
               'trail building':    '50/50',
               'backcountry skiing':'backcountry skiing',
               'moving snow':       '25/75',
               'Moving snow':       '25/75',
               'Resort skiing':     'Resort skiing',
               'Trottinette':       'cycling',
               'Trottinette ':       'cycling'
              }

keyToCoeff2 = {'cycling':             'cycling', 
               'lap_swimming':        'swimming', 
               'mountaineering':      'rock_climbing', 
               'open_water_swimming': 'swimming',
               'other':               'rock_climbing',
               'rock_climbing':       'rock_climbing',
               'strength_training':   'homeExercises', 
               'surfing_v2':          'swimming',
               'walking':             'walking'
               }

coeff = {'walking':           {'low_body': 1,    'high_body': 0},
         'cycling':           {'low_body': 1,    'high_body': 0.1},
         'swimming':          {'low_body': 0.1,  'high_body': 0.9},
         'rock_climbing':     {'low_body': 0.25, 'high_body': 0.75},
         '25/75':             {'low_body': 0.25, 'high_body': 0.75},
         'homeExercises':     {'low_body': 0.1,  'high_body': 0.9},
         '50/50':             {'low_body': 0.5,  'high_body': 0.5},
         'backcountry skiing':{'low_body': 0.75, 'high_body': 0.25},
         'Resort skiing':     {'low_body': 0.95, 'high_body': 0.05}
         }



##### Reloading data from past

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= cutoff_date]

data["swimSurfStrokes"] = 0


### Loading data from garmindb

with open("info.json", 'r') as json_file:
  info = json.load(json_file)
  

if extendedDataSaving:
  ### Loading data from garmindb
  # cnx = sqlite3.connect(info["pathToGarminSummaryDb"])
  # days_summary = pd.read_sql_query("SELECT * FROM days_summary", cnx)
  # cnx = sqlite3.connect(info["pathToGarminActivitiesDb"])
  # activities   = pd.read_sql_query("SELECT * FROM activities", cnx)
  ### Getting sleep data
  cnx = sqlite3.connect(info["pathToGarminDb"])
  sleep = pd.read_sql_query("SELECT * FROM sleep", cnx)
  sleep['timestamp'] = pd.to_datetime(sleep['day'])
  sleep.set_index('timestamp', inplace=True)
  data = data.merge(sleep, left_index=True, right_index=True, how='left')
  ### Getting rhr data
  daily_summary = pd.read_sql_query("SELECT * FROM daily_summary", cnx)
  daily_summary['timestamp'] = pd.to_datetime(daily_summary['day'])
  daily_summary.set_index('timestamp', inplace=True)
  data = data.merge(daily_summary, left_index=True, right_index=True, how='left')


cnx = sqlite3.connect(info["pathToGarminActivitiesDb"])
activities = pd.read_sql_query("SELECT * FROM activities", cnx)
activities.loc[activities['sport'] == 'generic', 'sport'] = activities.loc[activities['sport'] == 'generic', 'name']
activities['sport'] = activities['sport'].fillna('Other')


### Processing heart beats into lower and/or upper body load

cnx = sqlite3.connect(info["pathToGarminMonitoringDb"])

monitoring_hr = pd.read_sql_query("SELECT * FROM monitoring_hr", cnx)

monitoring_hr['timestamp'] = pd.to_datetime(monitoring_hr['timestamp'])
activities['start_time']   = pd.to_datetime(activities['start_time'])
activities['stop_time']    = pd.to_datetime(activities['stop_time'])

monitoring_hr = monitoring_hr[monitoring_hr['timestamp'] >= pd.to_datetime(cutoff_date)]

cliffJumpingAverageHeartRate = 90 # Garmin tracker is not worn during cliff jumping to avoid damaging the device
for activity in ['Cliff jumping', 'Cliff jumping ']:
  startStopTime = activities[activities["sport"] == activity][["start_time", "stop_time"]]
  for _, row in startStopTime.iterrows():
    start, stop = row['start_time'], row['stop_time']
    selectedTime = (monitoring_hr['timestamp'] >= start) & (monitoring_hr['timestamp'] <= stop)
    monitoring_hr.loc[selectedTime, 'heart_rate'] = cliffJumpingAverageHeartRate

for hr_id, heart_rate_active_threshold in enumerate(heart_rate_active_threshold_values):

  monitoring_hr["active_hr_" + str(heart_rate_active_threshold)] = 0
  monitoring_hr["act_hr_" + str(heart_rate_active_threshold) + "_lowBody"] = 0
  monitoring_hr["act_hr_" + str(heart_rate_active_threshold) + "_highBody"] = 0
  monitoring_hr = condensedAnalysisFunctions.addEmptyFieldForActivites(monitoring_hr, heart_rate_active_threshold, additionalActivities)
    
  monitoring_hr["active_hr_" + str(heart_rate_active_threshold)] = monitoring_hr["heart_rate"].copy() - heart_rate_active_threshold
  if True and hr_id < len(heart_rate_active_threshold_values) - 1:
    monitoring_hr["active_hr_" + str(heart_rate_active_threshold)][monitoring_hr["heart_rate"] > heart_rate_active_threshold_values[hr_id+1]] = heart_rate_active_threshold_values[hr_id+1] - heart_rate_active_threshold #0
    print(hr_id, "removed all bigger than", heart_rate_active_threshold_values[hr_id+1])
  monitoring_hr["active_hr_" + str(heart_rate_active_threshold)][monitoring_hr["heart_rate"] < heart_rate_active_threshold] = 0

  monitoring_hr["act_hr_" + str(heart_rate_active_threshold) + "_lowBody"] = monitoring_hr["active_hr_" + str(heart_rate_active_threshold)]


  for activity in np.unique(activities["sport"]):
    print(activity)
    startStopTime = activities[activities["sport"] == activity][["start_time", "stop_time", "cycles"]]
    for _, row in startStopTime.iterrows():
      start, stop = row['start_time'], row['stop_time']
      selectedTime = (monitoring_hr['timestamp'] >= start) & (monitoring_hr['timestamp'] <= stop)
      # Lower body load
      l_Coeff = coeff[keyToCoeff1[activity]]['low_body']
      monitoring_hr.loc[selectedTime, "act_hr_" + str(heart_rate_active_threshold) + "_lowBody"] = l_Coeff * monitoring_hr.loc[selectedTime, 'active_hr_' + str(heart_rate_active_threshold)]
      # Higher body load
      h_Coeff = coeff[keyToCoeff1[activity]]['high_body']
      monitoring_hr.loc[selectedTime, "act_hr_" + str(heart_rate_active_threshold) + "_highBody"] = h_Coeff * monitoring_hr.loc[selectedTime, 'active_hr_' + str(heart_rate_active_threshold)]
      # Number of surf and swim strokes
      if activity == "swimming":
        if type(row['cycles']) == float:
          if start.strftime('%Y-%m-%d') < str(data.index[-1]):
            data.loc[start.strftime('%Y-%m-%d'), 'swimSurfStrokes'] += row['cycles']
        else:
          print("Number of surf and swim strokes not added for", start)
      # Additional activities
      monitoring_hr = condensedAnalysisFunctions.addDataForActivities(monitoring_hr, selectedTime, heart_rate_active_threshold, additionalActivities, coeff, keyToCoeff1, activity)

  garminActivities = garminActivityDataGatheredFromWebExport(info["pathToGarminDataFromWebDIConnectFitness"])
  garminActivities['dateTimeEnd'] = garminActivities['dateTime'] + pd.to_timedelta(garminActivities['garminActivityDuration'], unit='ms').dt.floor('S')

  for activity in np.unique(garminActivities["garminActivityType"]):
    print(activity)
    startStopTime = garminActivities[garminActivities["garminActivityType"] == activity][["dateTime", "dateTimeEnd", "strokes"]]
    for _, row in startStopTime.iterrows():
      start, stop = row['dateTime'], row['dateTimeEnd']
      selectedTime = (monitoring_hr['timestamp'] >= start) & (monitoring_hr['timestamp'] <= stop)
      # Lower body load
      l_Coeff = coeff[keyToCoeff2[activity]]['low_body']
      monitoring_hr.loc[selectedTime, 'act_hr_' + str(heart_rate_active_threshold) + '_lowBody'] = l_Coeff * monitoring_hr.loc[selectedTime, 'active_hr_' + str(heart_rate_active_threshold)]
      # Higher body load
      h_Coeff = coeff[keyToCoeff2[activity]]['high_body']
      monitoring_hr.loc[selectedTime, 'act_hr_' + str(heart_rate_active_threshold) + '_highBody'] = h_Coeff * monitoring_hr.loc[selectedTime, 'active_hr_' + str(heart_rate_active_threshold)]
      # Number of surf and swim strokes
      if activity == 'lap_swimming' and start.strftime('%Y-%m-%d') >= cutoff_date:
        data.loc[start.strftime('%Y-%m-%d'), 'swimSurfStrokes'] += row['strokes']
      # Additional activities
      monitoring_hr = condensedAnalysisFunctions.addDataForActivities(monitoring_hr, selectedTime, heart_rate_active_threshold, additionalActivities, coeff, keyToCoeff2, activity)

### Get sum of daily values for lower and upper body load 

monitoring_hr['timestamp'] = pd.to_datetime(monitoring_hr['timestamp'])

monitoring_hr.set_index('timestamp', inplace=True)

daily_hr_data = monitoring_hr.resample('D').sum()[np.array([['active_hr_' + str(heart_rate_active_threshold), 'act_hr_' + str(heart_rate_active_threshold) + '_lowBody', 'act_hr_' + str(heart_rate_active_threshold) + '_highBody'] + condensedAnalysisFunctions.returnMonitoring_hr_Variables(additionalActivities, heart_rate_active_threshold) for heart_rate_active_threshold in heart_rate_active_threshold_values]).flatten().tolist()]

data = data.merge(daily_hr_data, left_index=True, right_index=True, how='left')

#
if replaceCyclingCaloriesByGarminCyclingHr:
  data['garminCyclingHr'] = data['act_hr_70_cycling_lowBody'] + data['act_hr_110_cycling_lowBody']

# Plotting per day

data["realTimeEyeInCar"] = data["realTimeEyeDrivingTime"] + data["realTimeEyeRidingTime"]
data["computerAndCarRealTime"] = data["realTimeEyeDrivingTime"] + data["manicTimeRealTime"] # SETTING TO DRIVING TIME ONLY

scaler = MinMaxScaler()
listOfVariables = ['realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain'] + np.array([['active_hr_' + str(heart_rate_active_threshold), 'act_hr_' + str(heart_rate_active_threshold) + '_lowBody', 'act_hr_' + str(heart_rate_active_threshold) + '_highBody'] for heart_rate_active_threshold in heart_rate_active_threshold_values]).flatten().tolist() + ['garminSteps', 'garminCyclingActiveCalories',  'realTimeEyeDrivingTime', 'realTimeEyeRidingTime', 'whatPulseRealTime', 'manicTimeRealTime', 'realTimeEyeInCar', 'computerAndCarRealTime', 'climbingDenivelation', 'climbingMaxEffortIntensity', 'garminClimbingActiveCalories', 'garminKneeRelatedActiveCalories', 'swimSurfStrokes']

if replaceCyclingCaloriesByGarminCyclingHr:
  listOfVariables += ['garminCyclingHr']


listOfVariables_scaled = [var + 'sca' for var in listOfVariables]

data[listOfVariables_scaled] = scaler.fit_transform(data[listOfVariables])

# data[listOfVariables_scaled].plot()
# plt.show()

# Rolling mean plotting

for variable in listOfVariables:
  data[variable + "_RollingMean"] = data[variable].rolling(rollingWindow).mean()

data[[var + "_RollingMean" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean" for var in listOfVariables]])


# Lower

lowBodyVars1 = ['act_hr_' + str(heart_rate_active_threshold_values[0]) + '_lowBody', 'act_hr_' + str(heart_rate_active_threshold_values[1]) + '_lowBody', 'realTimeKneePain']
if not(replaceCyclingCaloriesByGarminCyclingHr):
  lowBodyVars2 = ['garminSteps', 'garminCyclingActiveCalories', 'realTimeKneePain']
else:
  lowBodyVars2 = ['garminSteps', 'garminCyclingHr', 'realTimeKneePain']
lowBodyVars3 = ['realTimeEyeDrivingTime', 'manicTimeRealTime', 'realTimeKneePain']
colors_lowBodyVars1 = ['blue', 'orange', 'red']
colors_lowBodyVars2 = ['green', 'purple', 'red']
colors_lowBodyVars3 = ['cyan', 'black', 'red']
labels1 = ['hr' + str(heart_rate_active_threshold_values[0]), 'hr' + str(heart_rate_active_threshold_values[1]), 'knee']
if not(replaceCyclingCaloriesByGarminCyclingHr):
  labels2 = ['steps', 'cycleCal', 'knee']
else:
  labels2 = ['steps', 'cycleHr', 'knee']
labels3 = ['driving', 'computer', 'knee']

if True:
  lowBodyVars1 += ['garminKneeRelatedActiveCalories']
  colors_lowBodyVars1 += ['black']
  labels1 += ['cal']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=3, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
# data[[var + "_RollingMean" for var in lowBodyVars1]].plot(ax=axes[0], color=colors_lowBodyVars1, label=labels1)
for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left')
# data[[var + "_RollingMean" for var in lowBodyVars2]].plot(ax=axes[1], color=colors_lowBodyVars2, label=labels2)
for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left')
# data[[var + "_RollingMean" for var in lowBodyVars3]].plot(ax=axes[2], color=colors_lowBodyVars3, label=labels3)
for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left')
# plt.savefig('11_' + parameterOption['figName'] + '_a_low.' + figsFormat, format=figsFormat)
plt.show()


# Higher

highBodyVars1 = ['act_hr_' + str(heart_rate_active_threshold_values[0]) + '_highBody', 'act_hr_' + str(heart_rate_active_threshold_values[1]) + '_highBody', 'realTimeArmPain']
highBodyVars2 = ['whatPulseRealTime', 'realTimeArmPain']
highBodyVars3 = ['climbingDenivelation', 'climbingMaxEffortIntensity', 'garminClimbingActiveCalories', 'realTimeArmPain']
highBodyVars4 = ['swimSurfStrokes', 'realTimeArmPain']
colors_highBodyVars1 = ['blue', 'orange', 'red']  # Adjust the number of colors as needed
colors_highBodyVars2 = ['purple', 'red']
colors_highBodyVars3 = ['green', 'cyan', 'black', 'red']
colors_highBodyVars4 = ['olive', 'red']
labels1 = ['hr' + str(heart_rate_active_threshold_values[0]), 'hr' + str(heart_rate_active_threshold_values[1]), 'arm']
labels2 = ['clicks', 'arm']
labels3 = ['climbDen', 'climbMax', 'climbCal', 'arm']
labels4 = ['swimStrokes', 'arm']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=4, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
# data[[var + "_RollingMean" for var in highBodyVars1]].plot(ax=axes[0], color=colors_lowBodyVars1)
for col, color, label in zip([var + "_RollingMean" for var in highBodyVars1], colors_highBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left')
# data[[var + "_RollingMean" for var in highBodyVars2]].plot(ax=axes[1], color=colors_lowBodyVars2)
for col, color, label in zip([var + "_RollingMean" for var in highBodyVars2], colors_highBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left')
# data[[var + "_RollingMean" for var in highBodyVars3]].plot(ax=axes[1], color=colors_highBodyVars3)
for col, color, label in zip([var + "_RollingMean" for var in highBodyVars3], colors_highBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left')
# data[[var + "_RollingMean" for var in highBodyVars3]].plot(ax=axes[1], color=colors_highBodyVars3)
for col, color, label in zip([var + "_RollingMean" for var in highBodyVars4], colors_highBodyVars4, labels4):
  data[col].plot(ax=axes[3], color=color, label=label, linewidth=lineWidth)
axes[3].legend(loc='upper left')
# plt.savefig('11_' + parameterOption['figName'] + '_a_low.' + figsFormat, format=figsFormat)
plt.show()


# Face

faceVars1 = ['realTimeEyeDrivingTime', 'manicTimeRealTime', 'realTimeFacePain'] # DRIVING TIME ONLY NOT ALSO RIDING
faceVars2 = ['computerAndCarRealTime', 'realTimeFacePain']
colors_faceVars1 = ['green', 'blue', 'red']  # Adjust the number of colors as needed
colors_faceVars2 = ['purple', 'red']
labels1 = ['car', 'computer', 'face']
labels2 = ['car+computer', 'face']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=2, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
# data[[var + "_RollingMean" for var in faceVars1]].plot(ax=axes[0], color=colors_lowBodyVars1)
for col, color, label in zip([var + "_RollingMean" for var in faceVars1], colors_faceVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left')
# data[[var + "_RollingMean" for var in faceVars2]].plot(ax=axes[1], color=colors_lowBodyVars2)
for col, color, label in zip([var + "_RollingMean" for var in faceVars2], colors_faceVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left')
# plt.savefig('11_' + parameterOption['figName'] + '_a_low.' + figsFormat, format=figsFormat)
plt.show()


# OtherVariables
if len(additionalActivities):
  condensedAnalysisFunctions.plotAdditionalActivitiesAnalysis(data, heart_rate_active_threshold_values, additionalActivities, rollingWindow, figWidth, figHeight, hspace, lineWidth)


### Saving data

if True:
  
  listOfVariables = ['realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'active_hr_70', 'act_hr_70_lowBody', 'act_hr_70_highBody', 'active_hr_110', 'act_hr_110_lowBody', 'act_hr_110_highBody', 'garminSteps', 'garminCyclingActiveCalories',  'realTimeEyeDrivingTime', 'realTimeEyeRidingTime', 'whatPulseRealTime', 'manicTimeRealTime', 'realTimeEyeInCar', 'computerAndCarRealTime', 'climbingDenivelation', 'climbingMaxEffortIntensity', 'garminClimbingActiveCalories', 'garminKneeRelatedActiveCalories', 'swimSurfStrokes', 'act_hr_70_cycling_lowBody', 'act_hr_110_cycling_lowBody']
  
  # if len(additionalActivities):
    # listOfVariables += np.array([condensedAnalysisFunctions.returnMonitoring_hr_Variables(additionalActivities, heart_rate_active_threshold) for heart_rate_active_threshold in heart_rate_active_threshold_values]).flatten().tolist()
      
  if not(extendedDataSaving):
    data = data[listOfVariables]
  else:
    listOfVariables2 = listOfVariables + ['scooterRiding', 'realTimeSick', 'realTimeOtherPain', 'garminCliffJumpingActiveCalories', 'score', 'rhr'] #, 'generalmood']
    data = data[listOfVariables2]
    
    data[['scooterRiding', 'realTimeSick', 'realTimeOtherPain', 'garminCliffJumpingActiveCalories']] = data[['scooterRiding', 'realTimeSick', 'realTimeOtherPain', 'garminCliffJumpingActiveCalories']].replace([np.nan, np.inf, -np.inf], 0)
    for col in data.columns:
      # Step 1: if first row is missing, set it to the first available non-null value in the column
      if pd.isna(data.loc[data.index[0], col]):
        first_valid_index = data[col].first_valid_index()
        if first_valid_index is not None:  # make sure there's at least one non-null
          data.loc[data.index[0], col] = data.loc[first_valid_index, col]
      # Step 2: forward fill missing values
      data[col] = data[col].ffill()
  
  renaming = {
  'realTimeKneePain': 'kneePain', 
  'realTimeArmPain': 'armPain', 
  'realTimeFacePain': 'facePain', 
  'act_hr_70_cycling_lowBody': 'numberOfHeartBeatsBetween70and110_lowerBodyActivity_cycling', 
  'act_hr_110_cycling_lowBody': 'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling', 
  'active_hr_70': 'numberOfHeartBeatsBetween70and110', 
  'act_hr_70_lowBody': 'numberOfHeartBeatsBetween70and110_lowerBodyActivity', 
  'act_hr_70_highBody': 'numberOfHeartBeatsBetween70and110_upperBodyActivity', 
  'active_hr_110': 'numberOfHeartBeatsAbove110', 
  'act_hr_110_lowBody': 'numberOfHeartBeatsAbove110_lowerBodyActivity', 
  'act_hr_110_highBody': 'numberOfHeartBeatsAbove110_upperBodyActivity', 
  'garminSteps': 'numberOfSteps', 
  'garminCyclingActiveCalories': 'cyclingCalories',
  'realTimeEyeDrivingTime': 'timeSpentDriving', 
  'realTimeEyeRidingTime': 'timeSpentRidingCar', 
  'whatPulseRealTime': 'numberOfComputerClicksAndKeyStrokes', 
  'manicTimeRealTime': 'timeOnComputer', 
  'realTimeEyeInCar': 'timeInCar', 
  'computerAndCarRealTime': 'computerAndCarTime', 
  'climbingDenivelation': 'climbingDenivelation', 
  'climbingMaxEffortIntensity': 'climbingMaxEffortIntensity', 
  'garminClimbingActiveCalories': 'garminClimbingActiveCalories', 
  'garminKneeRelatedActiveCalories': 'garminKneeRelatedActiveCalories', 
  'swimSurfStrokes': 'swimAndSurfStrokes'
  }
  
  data = data.rename(columns=renaming)
  
  data.to_pickle('dataMay2023andLater.pkl')
  
  
  # Saving rolling mean variables
  
  if False:
  
    listOfVariables = data.columns
    
    for variable in listOfVariables:
      data[variable] = data[variable].rolling(rollingWindow).mean()

    data[[var for var in listOfVariables]] = scaler.fit_transform(data[[var for var in listOfVariables]])
    
    data = data.dropna()
    
    data.to_pickle('dataMay2023andLater_RollingMean.pkl')
    