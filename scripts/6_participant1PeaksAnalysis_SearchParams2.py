import pickle

import peaksAnalysisFunctions

# Reloading data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

plotGraphs = False
saveData   = False

for rollingMeanWindow in [7, 15, 21]:
  rollingMedianWindow = rollingMeanWindow
  for rollingMinMaxScalerWindow in [270, 360]:
    for minProminenceForPeakDetect in [0.01, 0.03, 0.05, 0.075, 0.1]:
      for windowForLocalPeakMinMaxFind in [5, 10, 15, 20]:
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
          [score, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays] = peaksAnalysisFunctions.calculateForAllRegions(data, parameters, plotGraphs, saveData)
          print("parameters:", parameters)
          print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount, "; regScore:", regScore)
          print("")
        except:
          print("problem occured")
          
