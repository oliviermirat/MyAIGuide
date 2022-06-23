import pickle

import peaksAnalysisFunctions

# Reloading data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Analysis parameters
parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 270, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.075, 'windowForLocalPeakMinMaxFind': 5, 'plotGraph': True, 'allBodyRegionsArmIncluded': False, 'plotZoomedGraph': False, 'minMaxTimeToleranceMinus': 0, 'minMaxTimeTolerancePlus': 0, 'plotGraphStrainDuringDescendingPain': False, 'zoomedGraphNbDaysMarginLeft': 14, 'zoomedGraphNbDaysMarginRight': 14}
# parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 270, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.03, 'windowForLocalPeakMinMaxFind': 3, 'plotGraph': True, 'allBodyRegionsArmIncluded': False, 'plotZoomedGraph': False, 'minMaxTimeToleranceMinus': 0, 'minMaxTimeTolerancePlus': 0, 'plotGraphStrainDuringDescendingPain': False}

plotGraphs = True
saveData   = True

[score, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays, nbPainPeaks] = peaksAnalysisFunctions.calculateForAllRegions(data, parameters, plotGraphs, saveData)
print("parameters:", parameters)
print("score:", score, "; totDaysTakenIntoAccount:", totDaysTakenIntoAccount)
print("regScore:", regScore)
print("nbAscendingDays: ", nbAscendingDays, "nbDescendingDays: ", nbDescendingDays)
print("nbPainPeaks:", nbPainPeaks)
print("")
print("nbAscendingDays: ", nbAscendingDays + nbPainPeaks * (parameters['minMaxTimeToleranceMinus'] + parameters['minMaxTimeTolerancePlus']), "nbDescendingDays: ", nbDescendingDays - nbPainPeaks * (parameters['minMaxTimeToleranceMinus'] + parameters['minMaxTimeTolerancePlus']))

