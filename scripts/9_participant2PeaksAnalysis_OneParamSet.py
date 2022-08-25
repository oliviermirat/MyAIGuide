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

import peaksAnalysisFunctions

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant2.txt", "rb")
data = pickle.load(input)
input.close()

data = data[data.index >= '2018-05-11']
data = data[data.index <= '2020-05-04']

plotBeforeAfter = False
if plotBeforeAfter:
  pd.set_option('display.max_rows', 10000)
  print(data["kneepain"])
  fig, axes = plt.subplots(nrows=2, ncols=1)
  axes[0].plot(data["kneepain"])
# Period 1
data.loc['2018-08-12':'2018-08-27', "kneepain"] = 3
# Period 2
data.loc['2018-11-19':'2018-11-21', "kneepain"] = 2
data.loc['2018-11-23':'2018-11-30', "kneepain"] = 2
# Period 3
data.loc['2019-02-13', "kneepain"] = 2
data.loc['2019-02-15':'2019-02-17', "kneepain"] = 2
data.loc['2019-02-18', "kneepain"] = 3
data.loc['2019-02-20', "kneepain"] = 3
# Period 4
data.loc['2019-06-21':'2019-06-30', "kneepain"] = 2 # 1.5
# Period 5
data.loc['2019-07-27':'2019-07-31', "kneepain"] = 3
data.loc['2019-08-03':'2019-08-09', "kneepain"] = 3
data.loc['2019-08-11':'2019-08-13', "kneepain"] = 3
data.loc['2019-08-15':'2019-08-18', "kneepain"] = 3.2
data.loc['2019-08-20', "kneepain"] = 3.2
# Period 6
data.loc['2019-09-25':'2019-10-16', "kneepain"] = 2 # 1.7
# Period 7
data.loc['2020-03-16':'2020-04-02', "kneepain"] = 2

withRolling = data["kneepain"].rolling(15, min_periods=1).mean().shift(int(-15/2))
for i in range(1, len(data["kneepain"])):
  if math.isnan(data["kneepain"][i]):
    data["kneepain"][i] = withRolling[i]
if plotBeforeAfter:
  axes[1].plot(data["kneepain"])
  plt.title("jjlllmmm")
  plt.show()


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
parameters = {'rollingMeanWindow': 21, 'rollingMinMaxScalerWindow': 60, 'rollingMedianWindow': 21, 'minProminenceForPeakDetect': 0.075, 'windowForLocalPeakMinMaxFind': 5, 'plotGraph': True, 'plotZoomedGraph': False, 'plotGraphStrainDuringDescendingPain': False, 'zoomedGraphNbDaysMarginLeft': 14, 'zoomedGraphNbDaysMarginRight': 14, 'minMaxTimeTolerancePlus': 1}

plotGraphs = True

peaksAnalysisFunctions.calculateForAllRegionsParticipant2(data, parameters, plotGraphs)

