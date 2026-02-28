import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')
import pickle
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import shutil
import peakAnalysis_main
import peakAnalysis_stats
import peakAnalysis_plot
from scipy import stats
# from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values

createFigs = False # This also needs to be changed in peakAnalysis_main
if createFigs:
  plt.rcParams.update({'font.size': 12})

def calculateForAllRegions(data, parameters, plotGraphs, saveData):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']
  plotZoomedGraph = parameters['plotZoomedGraph'] if 'plotZoomedGraph' in parameters else False
  allBodyRegionsArmIncluded = parameters['allBodyRegionsArmIncluded']
  minMaxTimeToleranceMinus = parameters['minMaxTimeToleranceMinus'] if 'minMaxTimeToleranceMinus' in parameters else 0
  minMaxTimeTolerancePlus  = parameters['minMaxTimeTolerancePlus'] if 'minMaxTimeTolerancePlus' in parameters else 0
  plotGraphStrainDuringDescendingPain = parameters['plotGraphStrainDuringDescendingPain'] if 'plotGraphStrainDuringDescendingPain' in parameters else False
  zoomedGraphNbDaysMarginLeft  = parameters['zoomedGraphNbDaysMarginLeft'] if 'zoomedGraphNbDaysMarginLeft' in parameters else 14
  zoomedGraphNbDaysMarginRight = parameters['zoomedGraphNbDaysMarginRight'] if 'zoomedGraphNbDaysMarginRight' in parameters else 14
  
  if os.path.isdir('./folderToSaveFigsIn'):
    shutil.rmtree('./folderToSaveFigsIn')
  os.mkdir('./folderToSaveFigsIn')
  
  data = data.rename(columns={'tracker_mean_distance': 'distance', 'tracker_mean_denivelation': 'denivelation', 'manicTimeDelta_corrected': 'timeOnComputer', 'whatPulseT_corrected': 'mouseAndKeyboardPressNb'})
  
  # Knee plots
  [maxstrainScoresKnee, maxstrainScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee] = peakAnalysis_main.visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, "kneePain", ["distance", "denivelation", "timeDrivingCar", "swimmingKm", "cycling"], [1, 1, 0.15, 1, 2], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight)

  # Finger hand arm plots
  if allBodyRegionsArmIncluded:
    [maxstrainScoresArm, maxstrainScores2Arm, totDaysAscendingPainArm, totDaysDescendingPainArm, dataArm, data2Arm, strainMinMaxAmplitudesArm, painMinMaxAmplitudesArm] = peakAnalysis_main.visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, "fingerHandArmPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata", "scooterRiding"], [1, 0.25, 0.5, 0.25, 0.7, 0.9, 0.8, 0.9], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight)

  # Forehead eyes plots
  [maxstrainScoresHead, maxstrainScores2Head, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, strainMinMaxAmplitudesHead, painMinMaxAmplitudesHead] = peakAnalysis_main.visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, "foreheadEyesPain", ["timeOnComputer", "timeDrivingCar"], [1, 0.8], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight)
  
  nbAscendingDays  = totDaysAscendingPainKnee + totDaysAscendingPainHead
  nbDescendingDays = totDaysDescendingPainKnee + totDaysDescendingPainHead

  # All regions together
  if allBodyRegionsArmIncluded:
    maxstrainScores = np.concatenate((np.concatenate((maxstrainScoresKnee, maxstrainScoresArm)), maxstrainScoresHead))
    strainMinMaxAmplitudes = np.concatenate((np.concatenate((strainMinMaxAmplitudesKnee, strainMinMaxAmplitudesArm)), strainMinMaxAmplitudesHead))
    painMinMaxAmplitudes   = np.concatenate((np.concatenate((painMinMaxAmplitudesKnee, painMinMaxAmplitudesArm)), painMinMaxAmplitudesHead))
    if plotGraphs:
      plt.hist(maxstrainScores)
      plt.show()
  else:
    # fig, axes = plt.subplots(nrows=2, ncols=1)
    maxstrainScores = np.concatenate((maxstrainScoresKnee, maxstrainScoresHead))
    strainMinMaxAmplitudes = np.concatenate((strainMinMaxAmplitudesKnee, strainMinMaxAmplitudesHead))
    painMinMaxAmplitudes   = np.concatenate((painMinMaxAmplitudesKnee, painMinMaxAmplitudesHead))
    
    statisticScores = peakAnalysis_stats.computeStatisticalSignificanceTests(maxstrainScores, nbDescendingDays, nbAscendingDays)
    
    if plotGraphs:
      peakAnalysis_plot.plotMaxStrainLocationInMinMaxCycle(maxstrainScores, nbDescendingDays, nbAscendingDays, createFigs)
  
  regScore = 0
  if True:
    reg = LinearRegression().fit(np.array([strainMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1))
    regScore = reg.score(np.array([strainMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1))
    if plotGraphs and not(createFigs):
      print("regression score:", regScore)
      pred = reg.predict(np.array([i for i in range(0, 10)]).reshape(-1, 1))
      fig3, axes = plt.subplots(nrows=1, ncols=1)
      plt.plot(strainMinMaxAmplitudes, painMinMaxAmplitudes, '.')
      plt.plot([i for i in range(0, 10)], pred)
      plt.xlabel('Strain Peak Amplitude')
      plt.ylabel('Pain Peak Amplitude')
      plt.xlim([0, 1])
      plt.ylim([0, 1])
      plt.show()
    
    strainAtZero          = (strainMinMaxAmplitudes == 0)
    painMinMaxAmplitudesNoStrain = painMinMaxAmplitudes[strainAtZero]
    painMinMaxAmplitudesWtStrain = painMinMaxAmplitudes[strainAtZero==False]
    print(str(len(painMinMaxAmplitudesNoStrain)) + " pain amplitudes (out of " + str(len(painMinMaxAmplitudesNoStrain) + len(painMinMaxAmplitudesWtStrain)) + ") had no strain peak preceding them ( " + str(( len(painMinMaxAmplitudesNoStrain) / (len(painMinMaxAmplitudesNoStrain) + len(painMinMaxAmplitudesWtStrain)) )*100) + " % )")
    
    if plotGraphs:
      peakAnalysis_plot.plotMaxPain(createFigs, painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain, painMinMaxAmplitudes)
  
  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    if allBodyRegionsArmIncluded:
      pickle.dump({'Knee': [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee], 'Arm': [maxstrainScoresArm, totDaysAscendingPainArm, totDaysDescendingPainArm, dataArm, data2Arm, strainMinMaxAmplitudesArm, painMinMaxAmplitudesArm], 'Head': [maxstrainScoresHead, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, strainMinMaxAmplitudesHead, painMinMaxAmplitudesHead]}, output)
    else:
      pickle.dump({'Knee': [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee], 'Head': [maxstrainScoresHead, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, strainMinMaxAmplitudesHead, painMinMaxAmplitudesHead]}, output)
    output.close()
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxstrainScores >= 0, maxstrainScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxstrainScores <= 0, maxstrainScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [statisticScores, nbAscendingDays + nbDescendingDays, regScore, nbAscendingDays, nbDescendingDays, len(painMinMaxAmplitudesNoStrain) + len(painMinMaxAmplitudesWtStrain)]


def calculateForAllRegionsParticipant2(data, parameters, plotGraphs, saveData=False):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']
  plotZoomedGraph = parameters['plotZoomedGraph'] if 'plotZoomedGraph' in parameters else False
  minMaxTimeToleranceMinus = parameters['minMaxTimeToleranceMinus'] if 'minMaxTimeToleranceMinus' in parameters else 0
  minMaxTimeTolerancePlus  = parameters['minMaxTimeTolerancePlus'] if 'minMaxTimeTolerancePlus' in parameters else 0
  plotGraphStrainDuringDescendingPain = parameters['plotGraphStrainDuringDescendingPain'] if 'plotGraphStrainDuringDescendingPain' in parameters else False
  zoomedGraphNbDaysMarginLeft  = parameters['zoomedGraphNbDaysMarginLeft'] if 'zoomedGraphNbDaysMarginLeft' in parameters else 14
  zoomedGraphNbDaysMarginRight = parameters['zoomedGraphNbDaysMarginRight'] if 'zoomedGraphNbDaysMarginRight' in parameters else 14
  
  if os.path.isdir('./folderToSaveFigsIn'):
    shutil.rmtree('./folderToSaveFigsIn')
  os.mkdir('./folderToSaveFigsIn')
  
  # Knee plots
  [maxstrainScoresKnee, maxstrainScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, strainMinMaxAmplitudes, painMinMaxAmplitudes] = peakAnalysis_main.visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, "kneepain", ["steps", "denivelation"], [1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight)
  
  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee

  maxstrainScores = maxstrainScoresKnee
  
  statisticScores = peakAnalysis_stats.computeStatisticalSignificanceTests(maxstrainScores, nbDescendingDays, nbAscendingDays)

  
  if plotGraphs:
    peakAnalysis_plot.plotMaxStrainLocationInMinMaxCycle(maxstrainScores, nbDescendingDays, nbAscendingDays, createFigs)

  strainAtZero          = (np.array(strainMinMaxAmplitudes) == 0)
  painMinMaxAmplitudes  = np.array(painMinMaxAmplitudes)
  painMinMaxAmplitudesNoStrain = painMinMaxAmplitudes[strainAtZero]
  painMinMaxAmplitudesWtStrain = painMinMaxAmplitudes[strainAtZero==False]
  
  painMinMaxAmpWtVsWithoutStrainStat = stats.ttest_ind(painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain)
  print("painMinMaxAmpWtVsWithoutStrain, ttest:", stats.ttest_ind(painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain))
  
  if plotGraphs:
    peakAnalysis_plot.plotMaxPain(createFigs, painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain, painMinMaxAmplitudes)

  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    pickle.dump({'Knee': [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee]}, output)
    output.close()
  
  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxstrainScores >= 0, maxstrainScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxstrainScores <= 0, maxstrainScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [statisticScores, nbAscendingDays + nbDescendingDays, painMinMaxAmpWtVsWithoutStrainStat.pvalue]


def calculateForAllRegionsParticipant8(data, parameters, plotGraphs, saveData=False):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']
  plotZoomedGraph = parameters['plotZoomedGraph'] if 'plotZoomedGraph' in parameters else False
  minMaxTimeToleranceMinus = parameters['minMaxTimeToleranceMinus'] if 'minMaxTimeToleranceMinus' in parameters else 0
  minMaxTimeTolerancePlus  = parameters['minMaxTimeTolerancePlus'] if 'minMaxTimeTolerancePlus' in parameters else 0
  plotGraphStrainDuringDescendingPain = parameters['plotGraphStrainDuringDescendingPain'] if 'plotGraphStrainDuringDescendingPain' in parameters else False
  zoomedGraphNbDaysMarginLeft  = parameters['zoomedGraphNbDaysMarginLeft'] if 'zoomedGraphNbDaysMarginLeft' in parameters else 14
  zoomedGraphNbDaysMarginRight = parameters['zoomedGraphNbDaysMarginRight'] if 'zoomedGraphNbDaysMarginRight' in parameters else 14
  
  if os.path.isdir('./folderToSaveFigsIn'):
    shutil.rmtree('./folderToSaveFigsIn')
  os.mkdir('./folderToSaveFigsIn')
  
  # Knee plots
  [maxstrainScoresKnee, maxstrainScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, strainMinMaxAmplitudes, painMinMaxAmplitudes] = peakAnalysis_main.visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, "kneepain", ["steps"], [1], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight)

  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee

  maxstrainScores = maxstrainScoresKnee
  
  statisticScores = peakAnalysis_stats.computeStatisticalSignificanceTests(maxstrainScores, nbDescendingDays, nbAscendingDays)
  
  if plotGraphs:
    peakAnalysis_plot.plotMaxStrainLocationInMinMaxCycle(maxstrainScores, nbDescendingDays, nbAscendingDays, createFigs)

  strainAtZero          = (np.array(strainMinMaxAmplitudes) == 0)
  painMinMaxAmplitudes  = np.array(painMinMaxAmplitudes)
  
  painMinMaxAmplitudesNoStrain = painMinMaxAmplitudes[strainAtZero]
  painMinMaxAmplitudesWtStrain = painMinMaxAmplitudes[strainAtZero==False]
  
  painMinMaxAmpWtVsWithoutStrainStat = stats.ttest_ind(painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain)
  print("painMinMaxAmpWtVsWithoutStrain, ttest:", stats.ttest_ind(painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain))
  
  if plotGraphs:
    peakAnalysis_plot.plotMaxPain(createFigs, painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain, painMinMaxAmplitudes)

  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    pickle.dump({'Knee': [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee]}, output)
    output.close()
  
  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxstrainScores >= 0, maxstrainScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxstrainScores <= 0, maxstrainScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [statisticScores, nbAscendingDays + nbDescendingDays, painMinMaxAmpWtVsWithoutStrainStat.pvalue]


def calculateForAllRegionsParticipant3_4_5_6_7_9(data, parameters, plotGraphs, stressorName, painRegionName, saveData=False):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']
  plotZoomedGraph = parameters['plotZoomedGraph'] if 'plotZoomedGraph' in parameters else False
  minMaxTimeToleranceMinus = parameters['minMaxTimeToleranceMinus'] if 'minMaxTimeToleranceMinus' in parameters else 0
  minMaxTimeTolerancePlus  = parameters['minMaxTimeTolerancePlus'] if 'minMaxTimeTolerancePlus' in parameters else 0
  
  # Knee plots
  [maxstrainScoresKnee, maxstrainScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, strainMinMaxAmplitudes, painMinMaxAmplitudes] = peakAnalysis_main.visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, painRegionName, [stressorName], [1], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus)

  maxstrainScores = maxstrainScoresKnee
  if plotGraphs:
    plt.hist(maxstrainScores, range=(-1, 1))
    plt.show()

  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    pickle.dump({'Knee': [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee]}, output)
    output.close()
  
  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxstrainScores >= 0, maxstrainScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxstrainScores <= 0, maxstrainScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [(nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays), nbAscendingDays + nbDescendingDays]
