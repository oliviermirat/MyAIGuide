import pickle
import sys
sys.path.insert(1, '../february2023ResearchGatePaperScripts')
import peaksAnalysis_launch

# Reloading data
input = open("./oldDataset.pkl", "rb")
data = pickle.load(input)
input.close()

# Analysis parameters
# 'minMaxTimeToleranceMinus' and 'minMaxTimeTolerancePlus' MUST both be set to 0 to generate the zoomed graphs for the 12_strainBuildUpFastRiseAndTriggersGraph.py graph!!!
parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 270, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.075, 'windowForLocalPeakMinMaxFind': 5, 'plotGraph': True, 'allBodyRegionsArmIncluded': False, 'plotZoomedGraph': False, 'minMaxTimeToleranceMinus': 0, 'minMaxTimeTolerancePlus': 0, 'plotGraphStrainDuringDescendingPain': False, 'zoomedGraphNbDaysMarginLeft': 14, 'zoomedGraphNbDaysMarginRight': 14}
# parameters = {'rollingMeanWindow': 15, 'rollingMinMaxScalerWindow': 270, 'rollingMedianWindow': 15, 'minProminenceForPeakDetect': 0.03, 'windowForLocalPeakMinMaxFind': 3, 'plotGraph': True, 'allBodyRegionsArmIncluded': False, 'plotZoomedGraph': False, 'minMaxTimeToleranceMinus': 0, 'minMaxTimeTolerancePlus': 0, 'plotGraphStrainDuringDescendingPain': False}

plotGraphs = True
saveData   = True

[score, totDaysTakenIntoAccount, regScore, nbAscendingDays, nbDescendingDays, nbPainPeaks] = peaksAnalysis_launch.calculateForAllRegions(data, parameters, plotGraphs, saveData)
print("parameters:", parameters)
print("totDaysTakenIntoAccount:", totDaysTakenIntoAccount)
print("regScore:", regScore)
print("nbAscendingDays: ", nbAscendingDays, "nbDescendingDays: ", nbDescendingDays)
print("nbPainPeaks:", nbPainPeaks)
print("")
print("nbAscendingDays: ", nbAscendingDays + nbPainPeaks * (parameters['minMaxTimeToleranceMinus'] + parameters['minMaxTimeTolerancePlus']), "nbDescendingDays: ", nbDescendingDays - nbPainPeaks * (parameters['minMaxTimeToleranceMinus'] + parameters['minMaxTimeTolerancePlus']))

