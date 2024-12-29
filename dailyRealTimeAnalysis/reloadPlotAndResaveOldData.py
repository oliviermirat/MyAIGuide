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

figWidth  = 20
figHeight = 5.1
hspace   = 0.4

with open("info.json", 'r') as json_file:
  info = json.load(json_file)

### Options

getDataFromGarminDb = True
garminDbStartDay    = "2023-12-18"

removeBlankScreenSaverTimes = True
addPhoneScreenTimes = True
includeCliffJumpingCalories = True
cliffJumpingActCaloPerMinute = 3.3 #2.7 # This might be a bit too conservative?

### Reloading data

inputt = open("../data/preprocessed/preprocessedMostImportantDataParticipant1_14-11-2023.txt", "rb")
data = pickle.load(inputt)
inputt.close()

# Minor fixes

data.loc[data.index < '2016-02-15', 'wholeArm'] = 2.8

if True:
  data = data[data.index >= '2017-01-01']

print(data.columns)

### Rolling mean and scaling

rollingWindow = 14

scaler = MinMaxScaler()

listOfVariables = ['tracker_mean_distance', 'tracker_mean_denivelation', 'cycling', 'manicTimeDelta_corrected', 'kneePain',   'climbingDenivelation', 'climbingMaxEffortIntensity', 'climbingMeanEffortIntensity', 'whatPulseT_corrected', 'swimmingKm', 'surfing', 'viaFerrata', 'scooterRiding', 'wholeArm',  'timeDrivingCar', 'manicTimeDelta_corrected', 'foreheadEyesPain', 'painInOtherRegion']

for variable in listOfVariables:
  data[variable + "_RollingMean"] = data[variable].rolling(rollingWindow).mean()

data[[var + "_RollingMean" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean" for var in listOfVariables]])

data[[var + "_Scaled" for var in listOfVariables]] = scaler.fit_transform(data[[var for var in listOfVariables]])


# Bonus

bonusVars1 = ['cycling', 'kneePain', 'wholeArm', 'foreheadEyesPain', 'painInOtherRegion']
colors_bonusVars1 = ['black', 'red', 'orange',  'purple', 'yellow']
labels1 = ['cycle', 'knee', 'arm', 'face', 'otherP']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=1, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean" for var in bonusVars1], colors_bonusVars1, labels1):
  data[col].plot(ax=axes, color=color, label=label)
axes.legend(loc='upper left')

plt.show()




# Knee

lowBodyVars1 = ['tracker_mean_distance', 'tracker_mean_denivelation', 'cycling', 'manicTimeDelta_corrected', 'kneePain']
colors_lowBodyVars1 = ['blue', 'orange', 'purple', 'black', 'red']
labels1 = ['dist', 'den', 'cycle', 'computer', 'knee']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=2, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_Scaled" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label)
axes[0].legend(loc='upper left')

for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
  data[col].plot(ax=axes[1], color=color, label=label)
axes[1].legend(loc='upper left')

plt.show()

# Arms

highBodyVars1 = ['climbingDenivelation', 'climbingMaxEffortIntensity', 'climbingMeanEffortIntensity', 'viaFerrata', 'wholeArm']
colors_highBodyVars1 = ['blue', 'orange', 'purple', 'black', 'red']
labels1 = ['climbDen', 'climbMax', 'climbMean', 'viaferrata', 'arm']

highBodyVars2 = ['whatPulseT_corrected', 'wholeArm']
colors_highBodyVars2 = ['green', 'red']
labels2 = ['clicks', 'arm']

highBodyVars3 = ['swimmingKm', 'surfing', 'wholeArm']
colors_highBodyVars3 = ['blue', 'orange', 'red']
labels3 = ['swim', 'surf', 'arm']

highBodyVars4 = ['scooterRiding', 'wholeArm']
colors_highBodyVars4 = ['purple', 'red']
labels4 = ['scooter', 'arm']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=4, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean" for var in highBodyVars1], colors_highBodyVars1, labels1):
  data[col].plot(ax=axes[0], color=color, label=label)
axes[0].legend(loc='upper left')

for col, color, label in zip([var + "_RollingMean" for var in highBodyVars2], colors_highBodyVars2, labels2):
  data[col].plot(ax=axes[1], color=color, label=label)
axes[1].legend(loc='upper left')

for col, color, label in zip([var + "_RollingMean" for var in highBodyVars3], colors_highBodyVars3, labels3):
  data[col].plot(ax=axes[2], color=color, label=label)
axes[2].legend(loc='upper left')

for col, color, label in zip([var + "_RollingMean" for var in highBodyVars4], colors_highBodyVars4, labels4):
  data[col].plot(ax=axes[3], color=color, label=label)
axes[3].legend(loc='upper left')

plt.show()


# Face

faceVars1 = ['timeDrivingCar', 'manicTimeDelta_corrected', 'foreheadEyesPain']
colors_faceVars1 = ['blue', 'orange',  'red']
labels1 = ['car', 'computer', 'face']

fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=1, ncols=1)
fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)

for col, color, label in zip([var + "_RollingMean" for var in faceVars1], colors_faceVars1, labels1):
  data[col].plot(ax=axes, color=color, label=label)
axes.legend(loc='upper left')

plt.show()





### Saving data

if True:
  
  listOfVariables = ['tracker_mean_distance', 'tracker_mean_denivelation', 'cycling', 'manicTimeDelta_corrected', 'kneePain',   'climbingDenivelation', 'climbingMaxEffortIntensity', 'climbingMeanEffortIntensity', 'whatPulseT_corrected', 'swimmingKm', 'surfing', 'viaFerrata', 'scooterRiding', 'wholeArm',  'timeDrivingCar', 'manicTimeDelta_corrected', 'foreheadEyesPain', 'painInOtherRegion', 'generalmood']
  
  data = data[listOfVariables]
  
  renaming = {
  'tracker_mean_distance': 'distanceWalked', 
  'tracker_mean_denivelation': 'denivelationWalked', 
  'cycling': 'numberOfRecordedStepsDuringCycling', 
  'manicTimeDelta_corrected': 'timeOnComputer', 
  'kneePain': 'kneePain',
  'climbingDenivelation': 'climbingDenivelation',
  'climbingMaxEffortIntensity': 'climbingMaxEffortIntensity',
  'climbingMeanEffortIntensity': 'climbingMeanEffortIntensity',
  'whatPulseT_corrected': 'numberOfComputerClicksAndKeyStrokes',
  'swimmingKm': 'swimmingKm',
  'surfing': 'surfing',
  'viaFerrata': 'viaFerrata',
  'scooterRiding': 'scooterRidingDistance',
  'wholeArm': 'armPain',
  'timeDrivingCar': 'timeDrivingCar',
  'foreheadEyesPain': 'facePain',
  'generalmood': 'generalmood'
  }
  
  data = data.rename(columns=renaming)
  
  data.to_pickle('dataBeforeMay2023.pkl')
