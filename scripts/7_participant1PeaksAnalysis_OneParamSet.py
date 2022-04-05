import pickle

import peaksAnalysisFunctions

# Reloading data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Analysis parameters
parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 360, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.05, 'windowForLocalPeakMinMaxFind': 15, 'plotGraph': True, 'allBodyRegionsArmIncluded': False}

plotGraphs = True
saveData   = True

[score, totDaysTakenIntoAccount] = peaksAnalysisFunctions.calculateForAllRegions(data, parameters, plotGraphs, saveData)
print("parameters:", parameters)
print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount)
print("")
