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

import peaksAnalysisFunctions

# Missing data filling technique: choose one of the methods bellow
rollingMean = False
lowestPain  = True

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant8.txt", "rb")
data = pickle.load(input)
input.close()

data = data[data.index >= '2019-08-12']
data = data[data.index <= '2020-12-27']

if rollingMean:
  withRolling = data["kneepain"].rolling(15, min_periods=1).mean().shift(int(-15/2))
  for i in range(1, len(data["kneepain"])):
    if math.isnan(data["kneepain"][i]):
      data["kneepain"][i] = withRolling[i]

if lowestPain:
  data["kneepain"] = data["kneepain"].fillna(3)

# Steps
# cols = ['steps', 'kneepain']
# for idx, val in enumerate(cols):
  # data[val] = data[val] #/ np.max(data[val])

totalSize = 4*4*4*4

d = {'rollingMeanWindow': [0.0 for i in range(0, totalSize)], 'rollingMedianWindow': [0.0 for i in range(0, totalSize)], 'rollingMinMaxScalerWindow': [0.0 for i in range(0, totalSize)], 'minProminenceForPeakDetect': [0.0 for i in range(0, totalSize)], 'windowForLocalPeakMinMaxFind': [0.0 for i in range(0, totalSize)], 'poissonPValue1': [0.0 for i in range(0, totalSize)], 'ratio1': [0.0 for i in range(0, totalSize)], 'totCount1': [0.0 for i in range(0, totalSize)], 'totRef1': [0.0 for i in range(0, totalSize)], 'poissonPValue2': [0.0 for i in range(0, totalSize)], 'ratio2': [0.0 for i in range(0, totalSize)], 'totCount2': [0.0 for i in range(0, totalSize)], 'totRef2': [0.0 for i in range(0, totalSize)], 'poissonPValue3': [0.0 for i in range(0, totalSize)], 'ratio3': [0.0 for i in range(0, totalSize)], 'totCount3': [0.0 for i in range(0, totalSize)], 'totRef3': [0.0 for i in range(0, totalSize)], 'painMinMaxAmpWtVsWithoutStrain': [0.0 for i in range(0, totalSize)]}
differentParameterCheck = pd.DataFrame(data=d)

i = 0

plotGraphs = False
saveData   = False

for rollingMeanWindow in [3, 7, 15, 21]:
  rollingMedianWindow = rollingMeanWindow
  for rollingMinMaxScalerWindow in [30, 60, 90, 120]:
    for minProminenceForPeakDetect in [0.01, 0.025, 0.05, 0.075]:
      for windowForLocalPeakMinMaxFind in [1, 3, 5, 7]:
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
            [statisticScores, totDaysTakenIntoAccount, painMinMaxAmpWtVsWithoutStrainStat] = peaksAnalysisFunctions.calculateForAllRegionsParticipant8(data, parameters, plotGraphs, saveData)
            print("painMinMaxAmpWtVsWithoutStrainStat:", painMinMaxAmpWtVsWithoutStrainStat)
            print("parameters:", parameters)
            print("statisticScores:", statisticScores, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount)
            print("")
            differentParameterCheck.loc[i]['rollingMeanWindow']            = rollingMeanWindow
            differentParameterCheck.loc[i]['rollingMinMaxScalerWindow']    = rollingMinMaxScalerWindow
            differentParameterCheck.loc[i]['rollingMedianWindow']          = rollingMedianWindow
            differentParameterCheck.loc[i]['minProminenceForPeakDetect']   = minProminenceForPeakDetect
            differentParameterCheck.loc[i]['windowForLocalPeakMinMaxFind'] = windowForLocalPeakMinMaxFind
            differentParameterCheck.loc[i]['poissonPValue1']               = statisticScores['poissonPValue1']
            differentParameterCheck.loc[i]['ratio1']                       = statisticScores['ratio1']
            differentParameterCheck.loc[i]['totCount1']                    = statisticScores['totCount1']
            differentParameterCheck.loc[i]['totRef1']                      = statisticScores['totRef1']
            differentParameterCheck.loc[i]['poissonPValue2']               = statisticScores['poissonPValue2']
            differentParameterCheck.loc[i]['ratio2']                       = statisticScores['ratio2']
            differentParameterCheck.loc[i]['totCount2']                    = statisticScores['totCount2']
            differentParameterCheck.loc[i]['totRef2']                      = statisticScores['totRef2']
            differentParameterCheck.loc[i]['poissonPValue3']               = statisticScores['poissonPValue3']
            differentParameterCheck.loc[i]['ratio3']                       = statisticScores['ratio3']
            differentParameterCheck.loc[i]['totCount3']                    = statisticScores['totCount3']
            differentParameterCheck.loc[i]['totRef3']                      = statisticScores['totRef3']
            differentParameterCheck.loc[i]['painMinMaxAmpWtVsWithoutStrain'] = painMinMaxAmpWtVsWithoutStrainStat
            i += 1
          except:
            print("problem occured")
            i += 1

if rollingMean:
  differentParameterCheck.to_pickle("./participant8DifferentParameters_rollingMean.pkl")

if lowestPain:
  differentParameterCheck.to_pickle("./participant8DifferentParameters_lowestPain.pkl")
