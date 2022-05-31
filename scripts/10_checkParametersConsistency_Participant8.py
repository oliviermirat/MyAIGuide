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
input = open("../data/preprocessed/preprocessedDataParticipant8.txt", "rb")
data = pickle.load(input)
input.close()

data = data[data.index >= '2019-08-12']
data = data[data.index <= '2020-12-27']

data["kneepain"] = data["kneepain"].fillna(3) # Need to improve this

# Steps
cols = ['steps', 'kneepain']
for idx, val in enumerate(cols):
  data[val] = data[val] #/ np.max(data[val])


totalSize = 3*3*4*3

d = {'rollingMeanWindow': [0.0 for i in range(0, totalSize)], 'rollingMedianWindow': [0.0 for i in range(0, totalSize)], 'rollingMinMaxScalerWindow': [0.0 for i in range(0, totalSize)], 'minProminenceForPeakDetect': [0.0 for i in range(0, totalSize)], 'windowForLocalPeakMinMaxFind': [0.0 for i in range(0, totalSize)], 'score': [0.0 for i in range(0, totalSize)]}
differentParameterCheck = pd.DataFrame(data=d)

i = 0

plotGraphs = False
saveData   = False

for rollingMeanWindow in [7, 15, 21]:
  rollingMedianWindow = rollingMeanWindow
  for rollingMinMaxScalerWindow in [60, 90, 120, 180]:
    for minProminenceForPeakDetect in [0.025, 0.05, 0.075]:
      for windowForLocalPeakMinMaxFind in [4, 7, 10]:
        if i < totalSize:
          print("i:", i, " out of:", totalSize)
          parameters = {
            'rollingMeanWindow' :            rollingMeanWindow,
            'rollingMinMaxScalerWindow' :    rollingMinMaxScalerWindow,
            'rollingMedianWindow' :          rollingMedianWindow,
            'minProminenceForPeakDetect' :   minProminenceForPeakDetect,
            'windowForLocalPeakMinMaxFind' : windowForLocalPeakMinMaxFind,
            'plotGraph' :                    False,
            'allBodyRegionsArmIncluded':     False
          }
          try:
            [score, totDaysTakenIntoAccount] = peaksAnalysisFunctions.calculateForAllRegionsParticipant8(data, parameters, plotGraphs, saveData)
            print("parameters:", parameters)
            print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount)
            print("")
            differentParameterCheck.loc[i]['rollingMeanWindow']            = rollingMeanWindow
            differentParameterCheck.loc[i]['rollingMinMaxScalerWindow']    = rollingMinMaxScalerWindow
            differentParameterCheck.loc[i]['rollingMedianWindow']          = rollingMedianWindow
            differentParameterCheck.loc[i]['minProminenceForPeakDetect']   = minProminenceForPeakDetect
            differentParameterCheck.loc[i]['windowForLocalPeakMinMaxFind'] = windowForLocalPeakMinMaxFind
            differentParameterCheck.loc[i]['score']                        = score
            i += 1
          except:
            print("problem occured")

differentParameterCheck.to_pickle("./participant8DifferentParameters.pkl")
