import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import pdb
import seaborn as sns
import time
import os
from pathlib import Path
import sys
sys.path.insert(1, '../src/MyAIGuide/data_combinedDataSource')
import pytz
from datetime import timedelta

from extract_Fitbit import extract_fitbit
from extract_TapLog import extract_taplog

fitbit_path = '../data/external/myaiguideconfidentialdata/Participant1/MyFitbitData/logqs/Physical-Activity'

###

for variable in ['calories', 'distance', 'heart_rate', 'steps', 'altitude']:
  startTime = time.time()
  df_fitbit_calories = extract_fitbit(fitbit_path, variable)
  df_fitbit_calories['dateTime'] = pd.to_datetime(df_fitbit_calories['dateTime'], format='%m/%d/%y %H:%M:%S')
  endTime = time.time()
  print("Ellapsed Time for", str(variable), ":", endTime - startTime)
  path_output_file = '../data/preprocessed/fitbit_' + variable + '.pkl'
  df_fitbit_calories.to_pickle(path_output_file)


###

path_sport  = '../data/raw/ParticipantData/Participant1/sport.csv'
path_taplog = ['../data/raw/ParticipantData/Participant1/TapLog2015_11_25until2018_08_29.csv', '../data/raw/ParticipantData/Participant1/TapLog2019-03-16until2019_10_27.csv', '../data/raw/ParticipantData/Participant1/TapLog2020_08_09until2022_07_30_andUntil14072023.csv']

df_taplog = extract_taplog(path_sport, path_taplog)

df_taplog['startTimestamp'] = pd.to_datetime(df_taplog['startTimestamp'], format="%Y-%m-%dT%H:%M:%S.%f%z", utc=True) #+ timedelta(hours=1)
df_taplog['endTimestamp']   = pd.to_datetime(df_taplog['endTimestamp'], format="%Y-%m-%dT%H:%M:%S.%f%z", utc=True)  #+ timedelta(hours=1)

path_output_file = '../data/preprocessed/taplog.pkl'
df_taplog.to_pickle(path_output_file)


###

variable = 'exercise'
startTime = time.time()
df_fitbit_exercise = extract_fitbit(fitbit_path, variable)
df_fitbit_exercise['startTime'] = pd.to_datetime(df_fitbit_exercise['startTime'], format='%m/%d/%y %H:%M:%S')
endTime = time.time()
print("Ellapsed Time for", str(variable), ":", endTime - startTime)
path_output_file = '../data/preprocessed/fitbit_' + variable + '.pkl'
df_fitbit_exercise = df_fitbit_exercise.sort_values(by='startTime')
# df_fitbit_exercise['activityName'] = df_fitbit_exercise['activityName'].str.replace('Ã©', 'e', regex=True)
# df_fitbit_exercise['activityName'] = df_fitbit_exercise['activityName'].str.replace('Ã', 'a', regex=True)
df_fitbit_exercise = df_fitbit_exercise[['activityName', 'calories', 'duration', 'steps', 'logType', 'startTime', 'duration']]
df_fitbit_exercise.to_pickle(path_output_file)
# df_fitbit_exercise.to_csv("fitbit_exercise.xls")

