# This scripts assumes that the dataframe has been created and saved in data.txt

import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import math
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values
from sklearn.preprocessing import MinMaxScaler

import peaksAnalysis_launch

# Missing data filling technique: choose of the methods bellow
rollingMean = False
lowestPain  = True

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant8.txt", "rb")
data = pickle.load(input)
input.close()

data = data[data.index >= '2019-08-12']
data = data[data.index <= '2020-12-27']


if rollingMean:
  plotBeforeAfter = False
  if plotBeforeAfter:
    fig, axes = plt.subplots(nrows=2, ncols=1)
    axes[0].plot(data["kneepain"])
  withRolling = data["kneepain"].rolling(15, min_periods=1).mean().shift(int(-15/2))
  for i in range(1, len(data["kneepain"])):
    if math.isnan(data["kneepain"][i]):
      data["kneepain"][i] = withRolling[i]
  if plotBeforeAfter:
    axes[1].plot(data["kneepain"])
    plt.title("jjlllmmm")
    plt.show()
    
if lowestPain:
  data["kneepain"] = data["kneepain"].fillna(3)

# Steps
cols = ['steps', 'kneepain']
for idx, val in enumerate(cols):
  data[val] = data[val] #/ np.max(data[val])

fig, axes = plt.subplots(nrows=2, ncols=1)
for idx, val in enumerate(cols):
  data[val].plot(ax=axes[idx])
  axes[idx].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()

# Analysis parameters
if rollingMean:
  parameters = {'rollingMeanWindow': 7, 'rollingMinMaxScalerWindow': 60, 'rollingMedianWindow': 3, 'minProminenceForPeakDetect': 0.03, 'windowForLocalPeakMinMaxFind': 3, 'plotGraph': True, 'plotZoomedGraph': False, 'plotGraphStrainDuringDescendingPain': False, 'zoomedGraphNbDaysMarginLeft': 14, 'zoomedGraphNbDaysMarginRight': 14}

if lowestPain:
  parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 90, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.03, 'windowForLocalPeakMinMaxFind': 5, 'plotGraph': True, 'plotZoomedGraph': False, 'plotGraphStrainDuringDescendingPain': False, 'zoomedGraphNbDaysMarginLeft': 14, 'zoomedGraphNbDaysMarginRight': 14}

plotGraphs = True

peaksAnalysis_launch.calculateForAllRegionsParticipant8(data, parameters, plotGraphs)

