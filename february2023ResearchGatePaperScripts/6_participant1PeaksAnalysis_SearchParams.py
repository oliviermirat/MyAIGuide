import pickle

import peaksAnalysis_launch

# Reloading data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

plotGraphs = False
saveData   = False

for rollingMeanWindow in [15, 30, 45, 90]:
  for rollingMinMaxScalerWindow in [90, 180, 360]:
    for rollingMedianWindow in [15, 30, 90]:
      for minProminenceForPeakDetect in [0.05, 0.1, 0.2]:
        for windowForLocalPeakMinMaxFind in [7, 15, 30]:
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
            [score, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays, nbPainPeaks] = peaksAnalysis_launch.calculateForAllRegions(data, parameters, plotGraphs, saveData)
            print("parameters:", parameters)
            print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount, "; regScore:", regScore)
            print("")
          except:
            print("problem occured")
          
