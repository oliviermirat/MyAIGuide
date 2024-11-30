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

##### Reloading data from past

cutoff_date = "2023-05-15"

data = pd.read_pickle('latestData.pkl')

data = data.loc[data.index >= cutoff_date]

saveFigs = False

figsFormat = 'png'
figWidth  = 20
figHeight = 5.1


### Loading data from garmindb

with open("info.json", 'r') as json_file:
  info = json.load(json_file)

cnx = sqlite3.connect(info["pathToGarminSummaryDb"])
days_summary = pd.read_sql_query("SELECT * FROM days_summary", cnx)

cnx = sqlite3.connect(info["pathToGarminActivitiesDb"])
activities   = pd.read_sql_query("SELECT * FROM activities", cnx)


### Processing heart beats into lower and/or upper body load

cnx = sqlite3.connect(info["pathToGarminDb"])

sleep = pd.read_sql_query("SELECT * FROM sleep", cnx)

sleep['timestamp'] = pd.to_datetime(sleep['day'])

sleep.set_index('timestamp', inplace=True)

data = data.merge(sleep, left_index=True, right_index=True, how='left')


####

daily_summary = pd.read_sql_query("SELECT * FROM daily_summary", cnx)

daily_summary['timestamp'] = pd.to_datetime(daily_summary['day'])

daily_summary.set_index('timestamp', inplace=True)

data = data.merge(daily_summary, left_index=True, right_index=True, how='left')


####

scaler = MinMaxScaler()

# listOfVariables = ['score', 'rhr', 'stress_avg', 'sweat_loss', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain']

for painVar in ['realTimeKneePain']: #['realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain']:

  listOfVariables = ['score', 'rhr', painVar]

  data[listOfVariables] = scaler.fit_transform(data[listOfVariables])

  # data[listOfVariables].plot()
  # plt.show()

  rollingWindow = 14

  for variable in listOfVariables:
    data[variable + "_RollingMean"] = data[variable].rolling(rollingWindow).mean()

  data[[var + "_RollingMean" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean" for var in listOfVariables]])


  data[[var + "_RollingMean" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean" for var in listOfVariables]])

  fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=2, ncols=1)
  
  labels = ['sleep', 'hrv', 'knee']
  # data[[var for var in listOfVariables]].plot(ax=axes[0])
  for col, label in zip([var for var in listOfVariables], labels):
    data[col].plot(ax=axes[0], label=label)
  # data[[var + "_RollingMean" for var in listOfVariables]].plot(ax=axes[1])
  for col, label in zip([var + "_RollingMean" for var in listOfVariables], labels):
    data[col].plot(ax=axes[1], label=label)
  
  axes[0].legend(loc='upper left')
  axes[1].legend(loc='upper left')
  
  if saveFigs:
    plt.savefig('12_' + painVar + '.' + figsFormat, format=figsFormat)
  else:
    # data[[var + "_RollingMean" for var in listOfVariables]].plot()
    plt.show()

