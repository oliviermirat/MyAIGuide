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

saveFigs = False
figWidth  = 20
figHeight = 5.1
hspace   = 0.4
lineWidth = 1 #2 #1
plotTheMiddlePlotAgainSeparately = False #True

rollingWindow = 14


### Reloading data from past

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= "2016-02-15"]

columns_to_update = ['realTimeOtherPain', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain']
data.loc['2023-04-09', columns_to_update] = data.loc['2023-04-08', columns_to_update]

data['meanPain'] = (data['realTimeKneePain'] + data['realTimeArmPain'] + data['realTimeFacePain']) / 3
data['maxPain'] = data[['realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain']].max(axis=1)


### Max of various activities:

data['garminNonCyclingKneeRelatedCalories'] = data['garminKneeRelatedActiveCalories'] - data['garminCyclingActiveCalories']

print(data[['garminCyclingActiveCalories', 'garminNonCyclingKneeRelatedCalories']].max())

max_dates = data[['garminCyclingActiveCalories', 'garminNonCyclingKneeRelatedCalories']].idxmax()
print(max_dates)


print(data[['garminSurfSwimActiveCalories', 'garminClimbingActiveCalories']].max())

max_dates = data[['garminSurfSwimActiveCalories', 'garminClimbingActiveCalories']].idxmax()
print(max_dates)


### Parsing generalmood

curYear = ""
curMonth = ""
curDay = ""
filename = "C:/Users/mirat/OneDrive/QS/1_manualLogs/6_moreStuff_november2016.ods"

data1 = pyexcel_ods.get_data(filename)
sheet_name = list(data1.keys())[0]
mood = pd.DataFrame(data1[sheet_name])

dictMood = {
  "Really Good": 8,
  "Good": 7,
  "Fine": 6,
  "Variable but mostly good": 5,
  "Ok, but also not really that great": 4,
  "Variable but mostly not great": 3,
  "Tired": 2,
  "Depressed": 1,
}

for i in range(len(mood)):
  if len(str(mood.loc[i, 0])):
    currentYear = mood.loc[i, 0]
  else:
    mood.loc[i, 0] = currentYear
  # Month
  if len(str(mood.loc[i, 1])):
    currentMonth = mood.loc[i, 1]
  else:
    mood.loc[i, 1] = currentMonth
  # Day
  if len(str(mood.loc[i, 2])):
    currentDay = mood.loc[i, 2]
  else:
    mood.loc[i, 2] = currentDay
  
  date = str(mood.loc[i, 0]) + "-" + str(mood.loc[i, 1]) + "-" + str(mood.loc[i, 2])
  
  if date in data.index and mood.loc[i, 3] in dictMood:
    data.loc[date, 'generalmood'] = dictMood[mood.loc[i, 3]]


### Making cycling data more homogeneous
data['garminCyclingActiveCalories'] = data['garminCyclingActiveCalories'].apply(
    lambda x: 1 if x > 250 else x / 250
)

data.index = pd.to_datetime(data.index)
data.loc[data.index > '2023-04-30', 'cycling'] = data.loc[data.index > '2023-04-30', 'garminCyclingActiveCalories']

data.loc[data.index > '2023-04-30', 'tracker_mean_distance'] = data.loc[data.index > '2023-04-30', 'garminSteps']

data['tracker_mean_distance'].fillna(data['tracker_mean_distance'].median(), inplace=True) # around march/july 2022 there are 4 nan values
data['tracker_mean_denivelation'].fillna(data['tracker_mean_denivelation'].median(), inplace=True) # around march/july 2022 there are 4 nan values

# data['cycling'] = data.apply(
    # lambda row: row['garminCyclingActiveCalories'] if row.index > pd.Timestamp('2023-04-30') else None, axis=1
# )
###

data['climbingMeanEffortIntensity'] -= 2
data['climbingMaxEffortIntensity']  -= 2

##


# Open water swimming kilometers often not recorded, compensating for that

valid_rows = data[(data['garminSurfSwimActiveCalories'] > 0) & 
                  (data['swimmingKm'] > 0) & 
                  (data['surfing'] == 0)]
medianCaloriesPerSwimmingKm = (valid_rows['garminSurfSwimActiveCalories'] / valid_rows['swimmingKm']).median() # MIGHT BE BETTER TO CALCULATE LOCAL MEDIANS LATER ON!!!

condition = (data['garminSurfSwimActiveCalories'] > 0) & \
            (data['swimmingKm'] == 0) & \
            (data['surfing'] == 0)

data.loc[condition, 'swimmingKm'] = data.loc[condition, 'garminSurfSwimActiveCalories'] / medianCaloriesPerSwimmingKm


##

data['newArmStress']  = 0
data['newFaceStress'] = 0
data['newKneeStress'] = 0

rollingWindow = 90

scaler = MinMaxScaler()
listOfVariables = ['painInOtherRegion', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'realTimeOtherPain', 'realTimeSick', 'generalmood', 'meanPain', 'manicTimeRealTime', 'manicTimeDelta_corrected', 'whatPulseT_corrected', 'tracker_mean_distance', 'tracker_mean_denivelation', 'climbingDenivelation', 'climbingMaxEffortIntensity','climbingMeanEffortIntensity', 'swimmingKm', 'surfing', 'viaFerrata', 'swimming', 'cycling', 'scooterRiding', 'whatPulseRealTime', 'realTimeEyeDrivingTime', 'garminSurfSwimActiveCalories', 'newArmStress', 'newFaceStress', 'newKneeStress'] #, 'atHome', 'stress',  'garminSurfSwimActiveCalories']

data.index = pd.to_datetime(data.index)
data.loc[data.index < '2018-07-25', 'whatPulseRealTime'] = data.loc[data.index < '2018-07-25', 'whatPulseT_corrected']
data.loc[data.index < '2021-05-12', 'manicTimeRealTime'] = data.loc[data.index < '2021-05-12', 'manicTimeDelta_corrected']

listOfVariables_scaled = [var + 'sca' for var in listOfVariables]

data[listOfVariables_scaled] = scaler.fit_transform(data[listOfVariables])

climbDenivCoeff      = 0.2
climbMaxEffortCoeff  = 2.8 #0.8 #2.8
swimCoeff            = 0.5 #1 #0.5
surfCoeff            = 1
scooterCoeff         = 0.5
nbClicksCoeff        = 0.5
data['newArmStress'] = climbDenivCoeff * data['climbingDenivelation' + 'sca'] + climbMaxEffortCoeff * data['climbingMaxEffortIntensity' + 'sca'] + swimCoeff * data['swimmingKm' + 'sca'] + surfCoeff * data['surfing' + 'sca'] + scooterCoeff * data['scooterRiding' + 'sca'] + nbClicksCoeff * data['whatPulseRealTime' + 'sca']

drivingCoeff = 0.5 #1 #0.5
computerTCoeff = 1
data['newFaceStress'] = drivingCoeff * data['realTimeEyeDrivingTime' + 'sca'] + computerTCoeff * data['manicTimeRealTime' + 'sca']

distanceCoeff = 1
cycleCoeff    = 3 #1 #3
compTimeCoeff = 1
data['newKneeStress'] = distanceCoeff * data['tracker_mean_distance' + 'sca'] + cycleCoeff * data['cycling' + 'sca'] + compTimeCoeff * data['manicTimeRealTime' + 'sca'] # + denivCoeff * data['tracker_mean_denivelation']

for variable in listOfVariables:
  data[variable + "_RollingMean2"] = data[variable].rolling(rollingWindow).mean()

data[[var + "_RollingMean2" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean2" for var in listOfVariables]])



### Plotting

# Function

def onlyOnePlot(lowBodyVars2, colors_lowBodyVars2, labels2, data, lineWidth, figWidth, figHeight, hspace):

  fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=1, ncols=1)
  fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)

  for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
    data[col].plot(ax=axes, color=color, label=label, linewidth=lineWidth)
  axes.legend(loc='upper left', bbox_to_anchor=(1, 1))

  plt.show()

  
# Arm

lowBodyVars1 = ['realTimeArmPain', 'climbingDenivelation', 'climbingMaxEffortIntensity', 'swimmingKm', 'surfing', 'scooterRiding', 'whatPulseRealTime'] #, 'garminSurfSwimActiveCalories']
colors_lowBodyVars1 = ['red', 'blue', 'green', 'black', 'cyan', 'orange', 'magenta'] #, 'purple']
labels1 = ['armPain', 'climbingDenivelation', 'climbingMaxEffort', 'swimmingKm', 'surfing', 'scooterRiding', 'computerClicks'] #, 'garminSurfSwimActiveCalories']

lowBodyVars2 = ['realTimeArmPain', 'newArmStress']
colors_lowBodyVars2 = ['red', 'blue']
labels2 = ['armPain', 'armStress']

lowBodyVars3 = ['realTimeKneePain', 'realTimeFacePain', 'realTimeSick', 'realTimeOtherPain', 'generalmood']
colors_lowBodyVars3 = ['red', 'orange', 'black', 'magenta', 'green']
labels3 = ['kneePain', 'facePain', 'sick', 'otherPain', 'mood']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=3, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

if plotTheMiddlePlotAgainSeparately:
  onlyOnePlot(lowBodyVars2, colors_lowBodyVars2, labels2, data, lineWidth, figWidth, figHeight, hspace)

# Face

lowBodyVars1 = ['realTimeFacePain', 'realTimeEyeDrivingTime', 'manicTimeRealTime']
colors_lowBodyVars1 = ['red', 'blue', 'green']
labels1 = ['facePain', 'driving', 'computer']

lowBodyVars2 = ['realTimeFacePain', 'newFaceStress']
colors_lowBodyVars2 = ['red', 'blue']
labels2 = ['facePain', 'faceStress']

lowBodyVars3 = ['realTimeKneePain', 'realTimeArmPain', 'realTimeSick', 'realTimeOtherPain', 'generalmood']
colors_lowBodyVars3 = ['red', 'orange', 'black', 'magenta', 'green']
labels3 = ['kneePain', 'armPain', 'sick', 'otherPain', 'mood']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=3, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

if plotTheMiddlePlotAgainSeparately:
  onlyOnePlot(lowBodyVars2, colors_lowBodyVars2, labels2, data, lineWidth, figWidth, figHeight, hspace)

# Knee

lowBodyVars1 = ['realTimeKneePain', 'tracker_mean_distance', 'cycling', 'manicTimeRealTime'] #, 'tracker_mean_denivelation']
colors_lowBodyVars1 = ['red', 'blue', 'green', 'black'] #, 'cyan']
labels1 = ['kneePain', 'walking', 'cycling', 'computerTime'] #, 'deniv']

lowBodyVars2 = ['realTimeKneePain', 'newKneeStress']
colors_lowBodyVars2 = ['red', 'blue']
labels2 = ['kneePain', 'kneeStress']

lowBodyVars3 = ['realTimeArmPain', 'realTimeFacePain', 'realTimeSick', 'realTimeOtherPain', 'generalmood']
colors_lowBodyVars3 = ['red', 'orange', 'black', 'magenta', 'green']
labels3 = ['armPain', 'facePain', 'sick', 'otherPain', 'mood']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=3, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

if plotTheMiddlePlotAgainSeparately:
  onlyOnePlot(lowBodyVars2, colors_lowBodyVars2, labels2, data, lineWidth, figWidth, figHeight, hspace)


### Mental and sick related variables

lowBodyVars1 = ['realTimeSick', 'generalmood', 'meanPain', 'realTimeOtherPain']
colors_lowBodyVars1 = ['blue', 'black', 'red', 'green']
labels1 = ['sick', 'mood', 'meanPain', 'otherPain']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=1, ncols=1)
# fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)
for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes, color=color, label=label, linewidth=lineWidth)
# axes.legend(loc='upper left')
axes.legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

#

lowBodyVars1 = ['realTimeSick', 'generalmood', 'meanPain', 'realTimeOtherPain']
colors_lowBodyVars1 = ['blue', 'black', 'red', 'green']
labels1 = ['sick', 'mood', 'meanPain', 'otherPain']

lowBodyVars2 = ['tracker_mean_distance', 'cycling']
colors_lowBodyVars2 = ['green', 'blue']
labels2 = ['walking', 'cycling']

lowBodyVars3 = ['climbingDenivelation', 'climbingMaxEffortIntensity', 'swimmingKm', 'surfing']
colors_lowBodyVars3 = ['blue', 'cyan', 'black', 'green']
labels3 = ['climbingDenivelation', 'climbingMaxEffort', 'swimmingKm', 'surfing']

lowBodyVars4 = ['whatPulseRealTime', 'manicTimeRealTime', 'realTimeEyeDrivingTime', 'scooterRiding']
colors_lowBodyVars4 = ['blue', 'cyan', 'black', 'green']
labels4 = ['computerTime', 'driving', 'computerClicks', 'scooterRiding']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=4, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars4], colors_lowBodyVars4, labels4):
  data[col].plot(ax=axes[3], color=color, label=label, linewidth=lineWidth)
axes[3].legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

#

lowBodyVars1 = ['realTimeSick', 'realTimeOtherPain', 'generalmood', 'meanPain'] #, 'manicTimeRealTime', 'manicTimeDelta_corrected']
colors_lowBodyVars1 = ['blue', 'green', 'black', 'red'] #, 'cyan', 'orange']
labels1 = ['sick', 'otherPain', 'mood', 'meanPain'] #, 'comp1', 'comp2']

lowBodyVars2 = ['realTimeKneePain', 'newKneeStress']
colors_lowBodyVars2 = ['red', 'blue']
labels2 = ['kneePain', 'kneeStress']

lowBodyVars3 = ['realTimeArmPain', 'newArmStress']
colors_lowBodyVars3 = ['red', 'blue']
labels3 = ['armPain', 'armStress']

lowBodyVars4 = ['realTimeFacePain', 'newFaceStress']
colors_lowBodyVars4 = ['red', 'blue']
labels4 = ['facePain', 'faceStress']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=4, ncols=1)
# fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.85, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
axes[0].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
axes[1].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
axes[2].legend(loc='upper left', bbox_to_anchor=(1, 1))

for col, color, label in zip([var + "_RollingMean2" for var in lowBodyVars4], colors_lowBodyVars4, labels4):
  data[col].plot(ax=axes[3], color=color, label=label, linewidth=lineWidth)
axes[3].legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()
