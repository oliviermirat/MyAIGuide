import pickle
import pandas as pd
import peaksAnalysisFunctions

# Reloading data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

plotGraphs = False
saveData   = False

totalSize = 3*3*5*4

d = {'rollingMeanWindow': [0.0 for i in range(0, totalSize)], 'rollingMedianWindow': [0.0 for i in range(0, totalSize)], 'rollingMinMaxScalerWindow': [0.0 for i in range(0, totalSize)], 'minProminenceForPeakDetect': [0.0 for i in range(0, totalSize)], 'windowForLocalPeakMinMaxFind': [0.0 for i in range(0, totalSize)], 'score': [0.0 for i in range(0, totalSize)]}
differentParameterCheck = pd.DataFrame(data=d)

i = 0

for rollingMeanWindow in [7, 15, 21]:
  rollingMedianWindow = rollingMeanWindow
  for rollingMinMaxScalerWindow in [180, 270, 360]:
    for minProminenceForPeakDetect in [0.03, 0.05, 0.075, 0.1, 0.15]:
      for windowForLocalPeakMinMaxFind in [3, 5, 10, 15]:
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
            [score, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays, nbPainPeaks] = peaksAnalysisFunctions.calculateForAllRegions(data, parameters, plotGraphs, saveData)
            print("parameters:", parameters)
            print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount, "; regScore:", regScore)
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

differentParameterCheck.to_pickle("./participant1DifferentParameters.pkl")
