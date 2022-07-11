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

d = {'rollingMeanWindow': [0.0 for i in range(0, totalSize)], 'rollingMedianWindow': [0.0 for i in range(0, totalSize)], 'rollingMinMaxScalerWindow': [0.0 for i in range(0, totalSize)], 'minProminenceForPeakDetect': [0.0 for i in range(0, totalSize)], 'windowForLocalPeakMinMaxFind': [0.0 for i in range(0, totalSize)], 'poissonPValue1': [0.0 for i in range(0, totalSize)], 'ratio1': [0.0 for i in range(0, totalSize)], 'totCount1': [0.0 for i in range(0, totalSize)], 'totRef1': [0.0 for i in range(0, totalSize)], 'poissonPValue2': [0.0 for i in range(0, totalSize)], 'ratio2': [0.0 for i in range(0, totalSize)], 'totCount2': [0.0 for i in range(0, totalSize)], 'totRef2': [0.0 for i in range(0, totalSize)], 'poissonPValue3': [0.0 for i in range(0, totalSize)], 'ratio3': [0.0 for i in range(0, totalSize)], 'totCount3': [0.0 for i in range(0, totalSize)], 'totRef3': [0.0 for i in range(0, totalSize)]}
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
            [statisticScores, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays, nbPainPeaks] = peaksAnalysisFunctions.calculateForAllRegions(data, parameters, plotGraphs, saveData)
            print("parameters:", parameters)
            print("statisticScores:", statisticScores, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount, "; regScore:", regScore)
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
            i += 1
          except:
            print("problem occured")

differentParameterCheck.to_pickle("./participant1DifferentParameters.pkl")
