import pickle

import peaksAnalysisFunctions

# Reloading data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Analysis parameters
parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 360, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.05, 'windowForLocalPeakMinMaxFind': 15, 'plotGraph': True, 'allBodyRegionsArmIncluded': False}
# parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 270, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.075, 'windowForLocalPeakMinMaxFind': 5, 'plotGraph': True, 'allBodyRegionsArmIncluded': False}

plotGraphs = True
saveData   = True

[score, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays] = peaksAnalysisFunctions.calculateForAllRegions(data, parameters, plotGraphs, saveData)
print("parameters:", parameters)
print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount)
print("regScore:", regScore)
print("nbAscendingDays: ", nbAscendingDays, "nbDescendingDays: ", nbDescendingDays)
print("")
