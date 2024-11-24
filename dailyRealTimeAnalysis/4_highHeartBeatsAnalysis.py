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


##### Parameters

onlyZone2 = {
  'heart_rate_active_threshold': 110,
  'heart_rate_active_threshold2':  0,
  'expFactorOnly': 0,
  'overflowFactor': 0,
  'overFlowPowerFactor': 0,
  'figName': 'a_onlyZone2'
}

loadOverflowThenCutOffLowBeats = {
  'heart_rate_active_threshold': 70,
  'heart_rate_active_threshold2':  50,
  'expFactorOnly': 0,
  'overflowFactor': 0.5,
  'overFlowPowerFactor': 0,
  'figName': 'b_loadOverflowThenCutOffLowBeats'
}

power2ThenLoadOverflowNoCutOff = {
  'heart_rate_active_threshold': 70,
  'heart_rate_active_threshold2':  0,
  'expFactorOnly': 2,
  'overflowFactor': 0.5,
  'overFlowPowerFactor': 0,
  'figName': 'c_power2ThenLoadOverflowNoCutOff'
}

parameterOptions = [onlyZone2, loadOverflowThenCutOffLowBeats, power2ThenLoadOverflowNoCutOff]
parameterOptions = [onlyZone2, loadOverflowThenCutOffLowBeats]

saveFigs = True
figWidth  = 20
figHeight = 5.1
hspace   = 0.4

figsFormat = 'png'

rollingWindow = 14

cutoff_date = "2023-05-15"

keyToCoeff1 = {'walking':           'walking',
               'cycling':           'cycling',
               'swimming':          'swimming',
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
               'backcountry skiing':'backcountry skiing'
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
         'homeExercises':     {'low_body': 0.1,  'high_body': 0.9},
         '50/50':             {'low_body': 0.5,  'high_body': 0.5},
         'backcountry skiing':{'low_body': 0.75,  'high_body': 0.25}
         }


for parameterOption in parameterOptions:

  ##### Reloading data from past

  data = pd.read_pickle('latestData.pkl')

  data = data.loc[data.index >= cutoff_date]


  ### Loading data from garmindb

  with open("info.json", 'r') as json_file:
    info = json.load(json_file)

  cnx = sqlite3.connect(info["pathToGarminActivitiesDb"])
  activities = pd.read_sql_query("SELECT * FROM activities", cnx)
  activities.loc[activities['sport'] == 'generic', 'sport'] = activities.loc[activities['sport'] == 'generic', 'name']
  activities['sport'] = activities['sport'].fillna('Other')


  ### Processing heart beats into lower and/or upper body load

  heart_rate_active_threshold  = parameterOption['heart_rate_active_threshold']
  heart_rate_active_threshold2 = parameterOption['heart_rate_active_threshold2']
  expFactorOnly                = parameterOption['expFactorOnly']
  overflowFactor               = parameterOption['overflowFactor']
  overFlowPowerFactor          = parameterOption['overFlowPowerFactor']

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
  
  monitoring_hr["active_hr"] = 0
  monitoring_hr["act_hr_lowBody"] = 0
  monitoring_hr["act_hr_highBody"] = 0

  monitoring_hr["active_hr"] = monitoring_hr["heart_rate"] - heart_rate_active_threshold
  monitoring_hr["active_hr"][monitoring_hr["heart_rate"] < heart_rate_active_threshold] = 0

  monitoring_hr["act_hr_lowBody"] = monitoring_hr["active_hr"]


  for activity in np.unique(activities["sport"]):
    print(activity)
    startStopTime = activities[activities["sport"] == activity][["start_time", "stop_time"]]
    for _, row in startStopTime.iterrows():
      start, stop = row['start_time'], row['stop_time']
      selectedTime = (monitoring_hr['timestamp'] >= start) & (monitoring_hr['timestamp'] <= stop)
      # Lower body load
      l_Coeff = coeff[keyToCoeff1[activity]]['low_body']
      monitoring_hr.loc[selectedTime, 'act_hr_lowBody'] = l_Coeff * monitoring_hr.loc[selectedTime, 'active_hr']
      # Higher body load
      h_Coeff = coeff[keyToCoeff1[activity]]['high_body']
      monitoring_hr.loc[selectedTime, 'act_hr_highBody'] = h_Coeff * monitoring_hr.loc[selectedTime, 'active_hr']


  garminActivities = garminActivityDataGatheredFromWebExport(info["pathToGarminDataFromWebDIConnectFitness"])
  garminActivities['dateTimeEnd'] = garminActivities['dateTime'] + pd.to_timedelta(garminActivities['garminActivityDuration'], unit='ms').dt.floor('S')

  for activity in np.unique(garminActivities["garminActivityType"]):
    print(activity)
    startStopTime = garminActivities[garminActivities["garminActivityType"] == activity][["dateTime", "dateTimeEnd"]]
    for _, row in startStopTime.iterrows():
      start, stop = row['dateTime'], row['dateTimeEnd']
      selectedTime = (monitoring_hr['timestamp'] >= start) & (monitoring_hr['timestamp'] <= stop)
      # Lower body load
      l_Coeff = coeff[keyToCoeff2[activity]]['low_body']
      monitoring_hr.loc[selectedTime, 'act_hr_lowBody'] = l_Coeff * monitoring_hr.loc[selectedTime, 'active_hr']
      # Higher body load
      h_Coeff = coeff[keyToCoeff2[activity]]['high_body']
      monitoring_hr.loc[selectedTime, 'act_hr_highBody'] = h_Coeff * monitoring_hr.loc[selectedTime, 'active_hr']


  ### Exponential only

  if expFactorOnly > 0:
    monitoring_hr['active_hr']       = monitoring_hr['active_hr'] ** expFactorOnly
    monitoring_hr['act_hr_lowBody']  = monitoring_hr['act_hr_lowBody'] ** expFactorOnly
    monitoring_hr['act_hr_highBody'] = monitoring_hr['act_hr_highBody'] ** expFactorOnly


  ### 'Overflow' load

  if overflowFactor > 0:
    for i in range(1, len(monitoring_hr)):
      ind = monitoring_hr.index[i]
      if overflowFactor * monitoring_hr['act_hr_lowBody'][ind-1] > 1: #10:
        monitoring_hr.loc[ind, 'act_hr_lowBody'] += overflowFactor * monitoring_hr['act_hr_lowBody'][ind-1]
      if overflowFactor * monitoring_hr['act_hr_highBody'][ind-1] > 1: #10:
        monitoring_hr.loc[ind, 'act_hr_highBody'] += overflowFactor * monitoring_hr['act_hr_highBody'][ind-1]
      if overFlowPowerFactor > 0:
        monitoring_hr.loc[ind, 'act_hr_lowBody']  = (monitoring_hr['act_hr_lowBody'][ind])**overFlowPowerFactor
        monitoring_hr.loc[ind, 'act_hr_highBody'] = (monitoring_hr['act_hr_highBody'][ind])**overFlowPowerFactor

  if heart_rate_active_threshold2 > 0:
    monitoring_hr["act_hr_lowBody"] = monitoring_hr["act_hr_lowBody"] - heart_rate_active_threshold2
    monitoring_hr["act_hr_lowBody"][monitoring_hr["act_hr_lowBody"] < heart_rate_active_threshold2] = 0
    monitoring_hr["act_hr_highBody"] = monitoring_hr["act_hr_highBody"] - heart_rate_active_threshold2
    monitoring_hr["act_hr_highBody"][monitoring_hr["act_hr_highBody"] < heart_rate_active_threshold2] = 0


  ### Get sum of daily values for lower and upper body load 

  monitoring_hr['timestamp'] = pd.to_datetime(monitoring_hr['timestamp'])

  monitoring_hr.set_index('timestamp', inplace=True)

  daily_hr_data = monitoring_hr.resample('D').sum()[['active_hr', 'act_hr_lowBody', 'act_hr_highBody']]

  data = data.merge(daily_hr_data, left_index=True, right_index=True, how='left')



  # Plotting per day

  scaler = MinMaxScaler()
  listOfVariables = ['realTimeKneePain', 'active_hr', 'act_hr_lowBody', 'act_hr_highBody', 'realTimeArmPain']


  listOfVariables_scaled = [var + 'sca' for var in listOfVariables]

  data[listOfVariables_scaled] = scaler.fit_transform(data[listOfVariables])

  # data[listOfVariables_scaled].plot()
  # plt.show()

  # Rolling mean plotting

  for variable in listOfVariables:
    data[variable + "_RollingMean"] = data[variable].rolling(rollingWindow).mean()

  data[[var + "_RollingMean" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean" for var in listOfVariables]])


  lowBodyVars = ['act_hr_lowBody', 'realTimeKneePain']

  if saveFigs:
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=2, ncols=1)
    fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
    data[[var + "sca" for var in lowBodyVars]].plot(ax=axes[0])
    data[[var + "_RollingMean" for var in lowBodyVars]].plot(ax=axes[1])
    plt.savefig('11_' + parameterOption['figName'] + '_a_low.' + figsFormat, format=figsFormat)
  else:
    data[[var + "_RollingMean" for var in lowBodyVars]].plot()
    plt.show()


  highBodyVars = ['act_hr_highBody', 'realTimeArmPain']

  if saveFigs:
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=2, ncols=1)
    fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
    data[[var + "sca" for var in highBodyVars]].plot(ax=axes[0])
    data[[var + "_RollingMean" for var in highBodyVars]].plot(ax=axes[1])
    plt.savefig('11_' + parameterOption['figName'] + '_b_high.' + figsFormat, format=figsFormat)
  else:
    data[[var + "_RollingMean" for var in highBodyVars]].plot()
    plt.show()
