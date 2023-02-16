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

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant2.txt", "rb")
data = pickle.load(input)
input.close()

data = data[data.index >= '2018-05-11']
data = data[data.index <= '2020-05-04']

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
data.loc['2019-09-25':'2019-10-16', "kneepain"] = 2
# Period 7
data.loc['2020-03-16':'2020-04-02', "kneepain"] = 2

withRolling = data["kneepain"].rolling(15, min_periods=1).mean().shift(int(-15/2))
for i in range(1, len(data["kneepain"])):
  if math.isnan(data["kneepain"][i]):
    data["kneepain"][i] = withRolling[i]


# Steps
cols = ['movessteps', 'cum_gain_walking', 'googlefitsteps', 'elevation_gain', 'oruxcumulatedelevationgain', 'kneepain']
for idx, val in enumerate(cols):
  data[val] = data[val] / np.max(data[val])

data["steps"]        = data[["movessteps", "googlefitsteps"]].max(axis=1)
data["denivelation"] = data[["cum_gain_walking", "elevation_gain", "oruxcumulatedelevationgain"]].max(axis=1)


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
            [statisticScores, totDaysTakenIntoAccount, painMinMaxAmpWtVsWithoutStrainStat] = peaksAnalysis_launch.calculateForAllRegionsParticipant8(data, parameters, plotGraphs, saveData)
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

differentParameterCheck.to_pickle("./participant2DifferentParameters.pkl")
