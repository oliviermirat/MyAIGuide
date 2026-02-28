# This scripts assumes that the dataframe has been created and saved in data.txt

import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values
from sklearn.preprocessing import MinMaxScaler
import math

# Getting data
inputt = open("../data/preprocessed/preprocessedDataParticipant1.txt", "rb")
data = pickle.load(inputt)
inputt.close()
print(data)

# Adding to the preprocessedDataParticipant1
if False:
  data['cyclingCalories'] = 0
  data['cyclingDuration'] = 0
  data['cyclingExtraCalories'] = 0
  googletimeline_fitbit = pd.read_pickle('../data/preprocessed/googletimeline_fitbit.pkl')
  cyclingRows = googletimeline_fitbit[googletimeline_fitbit["taplog_activity"] == "Cycling"]
  def remove_timezone(dt):
    return dt.replace(tzinfo=None) if dt else dt
  cyclingRows['startTimestamp'] = cyclingRows['startTimestamp'].apply(remove_timezone)
  cyclingRows['endTimestamp']   = cyclingRows['endTimestamp'].apply(remove_timezone)
  cyclingRows["TimeElapsed"] = (cyclingRows["endTimestamp"]-cyclingRows["startTimestamp"]).dt.total_seconds()/60
  # cyclingRows = cyclingRows[cyclingRows["TimeElapsed"] < 4*60]
  cyclingRows['date'] = cyclingRows['startTimestamp'].dt.date
  cyclingRows = cyclingRows[['date', 'steps_n', 'calories', 'meanHeartRate', 'TimeElapsed']]
  for i in range(0, len(cyclingRows)):
    if not(math.isnan(cyclingRows.iloc[i]['calories'])):
      data.loc[cyclingRows.iloc[i]['date'].strftime("%Y-%m-%d"), 'cyclingCalories'] += cyclingRows.iloc[i]['calories']
      data.loc[cyclingRows.iloc[i]['date'].strftime("%Y-%m-%d"), 'cyclingDuration'] += cyclingRows.iloc[i]['TimeElapsed']
      data.loc[cyclingRows.iloc[i]['date'].strftime("%Y-%m-%d"), 'cyclingExtraCalories'] += cyclingRows.iloc[i]['calories'] - (1.2 * cyclingRows.iloc[i]['TimeElapsed'] ) # About 1.2 calories burned per minute at rest

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant1_b.txt", "wb")
pickle.dump(data, output)
output.close()
