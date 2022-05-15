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

import peaksAnalysisFunctions

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant2.txt", "rb")
data = pickle.load(input)
input.close()

data = data[data.index >= '2018-05-11']
data = data[data.index <= '2020-05-04']

# data["kneepain"] = transformPain(data["kneepain"])
data["kneepain"] = data["kneepain"].fillna(1)

# Steps
cols = ['movessteps', 'cum_gain_walking', 'googlefitsteps', 'elevation_gain', 'oruxcumulatedelevationgain', 'kneepain']
for idx, val in enumerate(cols):
  data[val] = data[val] / np.max(data[val])

data["steps"]        = data[["movessteps", "googlefitsteps"]].max(axis=1)
data["denivelation"] = data[["cum_gain_walking", "elevation_gain", "oruxcumulatedelevationgain"]].max(axis=1)


fig, axes = plt.subplots(nrows=8, ncols=1)
cols = cols + ["steps", "denivelation"]
for idx, val in enumerate(cols):
  if val == 'oruxcumulatedelevationgain':
    data[val].plot(ax=axes[idx], color='green', marker='o', linestyle='dashed', markersize=2)
  else:
    data[val].plot(ax=axes[idx])
  axes[idx].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()

# Analysis parameters
parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 90, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.05, 'windowForLocalPeakMinMaxFind': 7, 'plotGraph': True, 'plotZoomedGraph': False, 'plotGraphStrainDuringDescendingPain': False}

plotGraphs = True

peaksAnalysisFunctions.calculateForAllRegionsParticipant2(data, parameters, plotGraphs)

