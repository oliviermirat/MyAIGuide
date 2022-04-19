import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values, rollingMinMaxScalerMeanShift

plotWithScaling = False

def addMinAndMax(data, regionName, plotFig, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind):
  
  scoreBasedOnAmplitude = False
  debugMode = False
  debugModeGeneral = False
  
  # Finding local min and max of pain and removing subsquent min/max not separated by respectively max/min
  pain = np.array(data[regionName+'_RollingMean_MinMaxScaler'].tolist())
  maxpeaks, properties = find_peaks(pain, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  minpeaks, properties = find_peaks(-pain, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  if True:
    if plotFig:
      print("Before double max peaks removal: len(maxpeaks):", len(maxpeaks))
      print("Before double min peaks removal: len(minpeaks):", len(minpeaks))
    # Removing "double max peaks"
    lastSeenWasMaxPeak = False
    for i in range(0, len(data)):
      if i in maxpeaks:
        if lastSeenWasMaxPeak:
          maxpeaks = maxpeaks[maxpeaks != i]
        lastSeenWasMaxPeak = True
      if i in minpeaks:
        lastSeenWasMaxPeak = False
    # Removing "double min peaks"
    lastSeenWasMinPeak = False
    for i in range(0, len(data)):
      if i in minpeaks:
        if lastSeenWasMinPeak:
          minpeaks = minpeaks[minpeaks != i]
        lastSeenWasMinPeak = True
      if i in maxpeaks:
        lastSeenWasMinPeak = False
    if plotFig:
      print("After double max peaks removal: len(maxpeaks):", len(maxpeaks))
      print("After double min peaks removal: len(minpeaks):", len(minpeaks))
  
  # Adding two columns in dataframe equal to pain values at min/max frame and to nan elsewhere
  data['max'] = float('nan')
  data['max'][maxpeaks] = data[regionName+'_RollingMean_MinMaxScaler'][maxpeaks].tolist()
  data['min'] = float('nan')
  data['min'][minpeaks] = data[regionName+'_RollingMean_MinMaxScaler'][minpeaks].tolist()
  
  # Finding stress min/max
  stress = np.array(data['regionSpecificStress_RollingMean_MinMaxScaler'].tolist())
  maxpeaksStress, properties = find_peaks(stress, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  minpeaksStress, properties = find_peaks(-stress, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  data['maxStress'] = float('nan')
  
  # Calculates for each stress peak the relative location in the min/max pain cycle
  negativeValue = 0
  positiveValue = 0
  # -1 : maxStress slightly above maxPain
  # 0  : maxStress at minPain
  # 1  : maxStress slightly below maxPain
  maxStressScores  = np.array([float('nan') for i in range(0, len(maxpeaksStress))])
  maxStressScores2 = np.array([float('nan') for i in range(0, len(maxpeaksStress))])
  for ind, maxStress in enumerate(maxpeaksStress):
    closestMaxPain = maxpeaks[np.argmin(abs(maxpeaks - maxStress))]
    keepMaxPeakStress = False
    if maxStress >= closestMaxPain: # maxStress >= closestMaxPain
      minPainCandidates = np.array([minPain for minPain in minpeaks if minPain >= closestMaxPain and maxStress <= minPain])
      if len(minPainCandidates):
        keepMaxPeakStress = True
        closestMinPain = minPainCandidates[0]
        # closestMaxPain <= maxStress <= closestMinPain
        if scoreBasedOnAmplitude:
          maxStressScores[ind] = (pain[maxStress] - pain[closestMinPain]) / (pain[closestMinPain] - pain[closestMaxPain]) # Negative value
          if maxStressScores[ind] < -1: maxStressScores[ind] = -1
          if maxStressScores[ind] >  0: maxStressScores[ind] = 0
        else:
          maxStressScores[ind] = (maxStress - closestMinPain) / (closestMinPain - closestMaxPain) # Negative value
        maxStressScores2[ind] = pain[maxStress+1] - pain[maxStress] if maxStress + 1 < len(pain) else 0
        if debugMode: print("Negative value:", maxStressScores[ind])
        negativeValue += 1
    else: # maxStress < closestMaxPain
      minPainCandidates = np.array([minPain for minPain in minpeaks if minPain <= closestMaxPain and minPain <= maxStress])
      if len(minPainCandidates):
        keepMaxPeakStress = True
        closestMinPain = minPainCandidates[-1:][0]
        # closestMinPain <= maxStress <= closestMaxPain
        if scoreBasedOnAmplitude:
          maxStressScores[ind] = (pain[maxStress] - pain[closestMinPain]) / (pain[closestMaxPain] - pain[closestMinPain]) # Positive value
          if maxStressScores[ind] > 1: maxStressScores[ind] = 1
          if maxStressScores[ind] < 0: maxStressScores[ind] = 0
        else:
          maxStressScores[ind] = (maxStress - closestMinPain) / (closestMaxPain - closestMinPain) # Positive value
        maxStressScores2[ind] = pain[maxStress+1] - pain[maxStress] if maxStress + 1 < len(pain) else 0
        if debugMode: print("Positive value:", maxStressScores[ind])
        positiveValue += 1
    if keepMaxPeakStress:
      data['maxStress'][maxStress - 1] = 0
      data['maxStress'][maxStress] = data['regionSpecificStress_RollingMean_MinMaxScaler'][maxStress]
      data['maxStress'][maxStress + 1] = 0
  if debugModeGeneral: print("negativeValue:", negativeValue)
  if debugModeGeneral: print("positiveValue:", positiveValue)
  
  # Calculating total number of days where the pain is respectively ascending and descending
  minPeak = minpeaks[0]
  totDaysAscendingPain  = 0
  totDaysDescendingPain = 0
  toAddAscending  = []
  toAddDescending = []
  for maxPeak in maxpeaks:
    if minPeak < maxPeak:
      toAddAscending.append(maxPeak - minPeak)
      # totDaysAscendingPain += maxPeak - minPeak
      if debugMode: print("should be positive 1: ", maxPeak - minPeak)
    minPeakCandidates = np.array([minPain for minPain in minpeaks if minPain >= maxPeak])
    if len(minPeakCandidates):
      minPeak = minPeakCandidates[0]
      toAddDescending.append(minPeak - maxPeak)
      # totDaysDescendingPain += minPeak - maxPeak
      if debugMode: print("should be positive 2: ", minPeak - maxPeak)
    else:
      minPeak = -1
  totDaysAscendingPain = np.sum(np.array(toAddAscending[1:-1]))
  totDaysDescendingPain = np.sum(np.array(toAddDescending[1:-1]))
  if debugModeGeneral: print("totDaysAscendingPain:", totDaysAscendingPain)
  if debugModeGeneral: print("totDaysDescendingPain:", totDaysDescendingPain)
  
  # Plotting for each stress peak the relative location in the min/max pain cycle
  if plotFig:
    fig2, axes = plt.subplots(nrows=1, ncols=1)
    sns.stripplot(y="col1", data=pd.DataFrame(data={'col1': maxStressScores}), size=4, color=".3", linewidth=0)
    plt.show()
    fig2, axes = plt.subplots(nrows=1, ncols=1)
    plt.hist(maxStressScores)
    plt.show()
  
  # Stress peaks amplitudes vs Pain peaks amplitudes: calculating values
  painMinMaxAmplitudes   = []
  stressMinMaxAmplitudes = []
  if True:
    minMaxTimeTolerance    = 7
    analyzeStressResponseAfter = False
    for maxPainPeak in maxpeaks:
      minPainCandidates = np.array([minPainPeak for minPainPeak in minpeaks if minPainPeak <= maxPainPeak])
      if len(minPainCandidates):
        minPainPeak = minPainCandidates[-1]
        correspondingStressPeakCandidates = [maxStress for maxStress in maxpeaksStress if maxStress >= minPainPeak - minMaxTimeTolerance and maxStress <= maxPainPeak + minMaxTimeTolerance]
        if len(correspondingStressPeakCandidates):
          maxStressPeak = correspondingStressPeakCandidates[np.argmax([stress[maxStress] for maxStress in correspondingStressPeakCandidates])]
          minStressCandidates = np.array([minStressPeak for minStressPeak in minpeaks if minStressPeak <= maxStressPeak]) if not(analyzeStressResponseAfter) else np.array([minStressPeak for minStressPeak in minpeaks if minStressPeak >= maxStressPeak])
          if len(minStressCandidates):
            minStressPeak = minStressCandidates[-1] if not(analyzeStressResponseAfter) else minStressCandidates[0]
            painMinMaxAmplitudes.append(pain[maxPainPeak] - pain[minPainPeak])
            stressMinMaxAmplitudes.append(stress[maxStressPeak] - stress[minStressPeak])
            if plotFig:
              print("date: ", data.index[maxPainPeak], "; pain: ", pain[maxPainPeak] - pain[minPainPeak], "; stress: ", stress[maxStressPeak] - stress[minStressPeak])
        else:
          painMinMaxAmplitudes.append(pain[maxPainPeak] - pain[minPainPeak])
          stressMinMaxAmplitudes.append(0)
          if plotFig:
            print("date: ", data.index[maxPainPeak], "; pain: ", pain[maxPainPeak] - pain[minPainPeak], "; stress: ", 0)
  
  if plotFig:
    print("max:", [data.index[peak] for peak in maxpeaks])
    print("min:", [data.index[peak] for peak in minpeaks])
  
  return [maxStressScores, totDaysAscendingPain, totDaysDescendingPain, minpeaks, maxpeaks, maxStressScores2, stressMinMaxAmplitudes, painMinMaxAmplitudes]



def prepareForPlotting(data, region, minpeaks, maxpeaks):
  
  data['painAscending']  = data[region + '_RollingMean_MinMaxScaler']
  data['painDescending'] = data[region + '_RollingMean_MinMaxScaler']
  data['maxStress2']     = data['maxStress']
  
  allPeaks = np.concatenate((minpeaks, maxpeaks))
  ascending = True
  ascendingElement  = [0 for i in range(0, len(data))]
  descendingElement = [0 for i in range(0, len(data))]
  if min(allPeaks) in maxpeaks:
    ascending = False
  for i in range(min(allPeaks), max(allPeaks)):
    if i in maxpeaks:
      ascending = False
    if i in minpeaks:
      ascending = True
    if ascending:
      ascendingElement[i] = 1
    else:
      descendingElement[i] = 1
  
  data['painAscending'][[ind for ind, val in enumerate(descendingElement) if val or ind < min(allPeaks) or ind > max(allPeaks)]] = float('nan')
  data['painDescending'][[ind for ind, val in enumerate(ascendingElement) if val or ind < min(allPeaks) or ind > max(allPeaks)]] = float('nan')
  data['maxStress2'][[ind for ind in range(0, len(data)) if ind < min(allPeaks) or ind > max(allPeaks)]] = float('nan')
  
  data = data.drop(columns=[region + '_RollingMean_MinMaxScaler', 'max', 'min', 'maxStress', 'regionSpecificStress_RollingMean_MinMaxScaler'])
  
  return data

def plottingOptions(axes, axesNum, text, legendsText, locLegend, sizeLegend):
  if legendsText:
    axes[axesNum].legend(legendsText, loc=locLegend, bbox_to_anchor=(1, 0.5))#, prop={'size': sizeLegend})
  else:
    if plotWithScaling:
      axes[axesNum].legend(loc=locLegend, prop={'size': sizeLegend})
    else:
      axes[axesNum].legend(loc=locLegend, bbox_to_anchor=(1, 0.5))#, prop={'size': sizeLegend})
  axes[axesNum].title.set_text(text)
  if plotWithScaling:
    axes[axesNum].title.set_fontsize(5)
  axes[axesNum].title.set_position([0.5, 0.93])
  axes[axesNum].get_xaxis().set_visible(False)

def visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(data, region, list_of_stressors, stressor_coef, window, window2, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph):
  
  if plotGraph:
    fig, axes = plt.subplots(nrows=5, ncols=1)
    fig.suptitle(region, fontsize=8)
  scaler = MinMaxScaler()
  
  # Plotting potential stressors causing pain in region
  data[list_of_stressors] = scaler.fit_transform(data[list_of_stressors])
  if plotGraph:
    data[list_of_stressors].plot(ax=axes[0], linestyle='', marker='o', markersize=0.5)
    plottingOptions(axes, 0, 'Stressors causing ' + region, [], 'upper right' if plotWithScaling else 'center left', 3 if plotWithScaling else 8)

  # Plotting stress and pain
  stress_and_pain = ["regionSpecificStress", region]
  data["regionSpecificStress"] = np.zeros(len(data[list_of_stressors[0]]))
  for idx, stressor in enumerate(list_of_stressors):
    data["regionSpecificStress"] = data["regionSpecificStress"] + stressor_coef[idx] * data[stressor]
  data[stress_and_pain] = scaler.fit_transform(data[stress_and_pain])
  if plotGraph:
    data[stress_and_pain].plot(ax=axes[1], linestyle='', marker='o', markersize=0.5)
    plottingOptions(axes, 1, 'Combined Stress (linear combination of previous stressors) and pain', ['stress', 'pain'], 'center left', 8)

  # Plotting Rolling Mean of stress and pain
  for var in stress_and_pain:
    data[var + "_RollingMean"] = data[var].rolling(window).mean()
  stress_and_pain_rollingMean = [name + "_RollingMean" for name in stress_and_pain]
  data[stress_and_pain_rollingMean] = scaler.fit_transform(data[stress_and_pain_rollingMean])
  if plotGraph:
    data[stress_and_pain_rollingMean].plot(ax=axes[2])
    plottingOptions(axes, 2, 'Rolling mean of combined stress and pain', ['stress', 'pain'], 'center left', 8)
  
  # Plotting Rolling MinMaxScaler of Rolling Mean of stress and pain
  stress_and_pain_RollingMean_MinMaxScaler = [name + "_MinMaxScaler" for name in stress_and_pain_rollingMean]
  for columnName in stress_and_pain_rollingMean:
    data[columnName + "_MinMaxScaler"] = rollingMinMaxScalerMeanShift(data, columnName, window2, window)
  if plotGraph:
    data[stress_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[3])
    plottingOptions(axes, 3, 'Rolling MinMaxScaler of rolling mean of combined stress and pain', ['stress', 'pain'], 'center left', 8)

  # Peaks analysis
  data2 = data[stress_and_pain_RollingMean_MinMaxScaler].copy()
  data2 = data2.rolling(rollingMedianWindow).median()
  [maxStressScores, totDaysAscendingPain, totDaysDescendingPain, minpeaks, maxpeaks, maxStressScores2, stressMinMaxAmplitudes, painMinMaxAmplitudes] = addMinAndMax(data2, region, False, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind)
  data2 = prepareForPlotting(data2, region, minpeaks, maxpeaks)
  if plotGraph:
    data2.plot(ax=axes[4])
    plottingOptions(axes, 4, "Peaks Analysis", ['painAscending', 'painDescending', 'PeakStress'], 'center left', 8)

  # Showing the final plot
  if plotGraph:
    plt.show()
  
  # Linear regression between stress and pain amplitudes
  if True:
    reg = LinearRegression().fit(np.array([stressMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1))
    if plotGraph:
      print("regression score:", reg.score(np.array([stressMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1)))
    pred = reg.predict(np.array([i for i in range(0, 10)]).reshape(-1, 1))
    if plotGraph:
      fig3, axes = plt.subplots(nrows=1, ncols=1)
      plt.plot(stressMinMaxAmplitudes, painMinMaxAmplitudes, '.')
      plt.plot([i for i in range(0, 10)], pred)
      plt.xlim([0, 1])
      plt.ylim([0, 1])
      plt.show()
  
  return [maxStressScores, maxStressScores2, totDaysAscendingPain, totDaysDescendingPain, data, data2, stressMinMaxAmplitudes, painMinMaxAmplitudes]


def calculateForAllRegions(data, parameters, plotGraphs, saveData):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']
  allBodyRegionsArmIncluded = parameters['allBodyRegionsArmIncluded']

  # Knee plots
  [maxStressScoresKnee, maxStressScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, stressMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee] = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(data, "kneePain", ["tracker_mean_distance", "tracker_mean_denivelation", "timeDrivingCar", "swimmingKm", "cycling"], [1, 1, 0.15, 1, 0.5], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph)

  # Finger hand arm plots
  if allBodyRegionsArmIncluded:
    [maxStressScoresArm, maxStressScores2Arm, totDaysAscendingPainArm, totDaysDescendingPainArm, dataArm, data2Arm, stressMinMaxAmplitudesArm, painMinMaxAmplitudesArm] = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(data, "fingerHandArmPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata", "scooterRiding"], [1, 0.25, 0.5, 0.25, 0.7, 0.9, 0.8, 0.9], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph)

  # Forehead eyes plots
  [maxStressScoresHead, maxStressScores2Head, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, stressMinMaxAmplitudesHead, painMinMaxAmplitudesHead] = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(data, "foreheadEyesPain", ["manicTimeDelta_corrected", "timeDrivingCar"], [1, 0.8], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph)

  # All regions together
  if allBodyRegionsArmIncluded:
    maxStressScores = np.concatenate((np.concatenate((maxStressScoresKnee, maxStressScoresArm)), maxStressScoresHead))
    stressMinMaxAmplitudes = np.concatenate((np.concatenate((stressMinMaxAmplitudesKnee, stressMinMaxAmplitudesArm)), stressMinMaxAmplitudesHead))
    painMinMaxAmplitudes   = np.concatenate((np.concatenate((painMinMaxAmplitudesKnee, painMinMaxAmplitudesArm)), painMinMaxAmplitudesHead))
    if plotGraphs:
      plt.hist(maxStressScores)
      plt.show()
  else:
    # fig, axes = plt.subplots(nrows=2, ncols=1)
    maxStressScores = np.concatenate((maxStressScoresKnee, maxStressScoresHead))
    stressMinMaxAmplitudes = np.concatenate((stressMinMaxAmplitudesKnee, stressMinMaxAmplitudesHead))
    painMinMaxAmplitudes   = np.concatenate((painMinMaxAmplitudesKnee, painMinMaxAmplitudesHead))
    if plotGraphs:
      plt.hist(maxStressScores)
      plt.show()
      
  regScore = 0
  if True:
    reg = LinearRegression().fit(np.array([stressMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1))
    regScore = reg.score(np.array([stressMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1))
    if plotGraphs:
      print("regression score:", regScore)
      pred = reg.predict(np.array([i for i in range(0, 10)]).reshape(-1, 1))
      fig3, axes = plt.subplots(nrows=1, ncols=1)
      plt.plot(stressMinMaxAmplitudes, painMinMaxAmplitudes, '.')
      plt.plot([i for i in range(0, 10)], pred)
      plt.xlim([0, 1])
      plt.ylim([0, 1])
      plt.show()
  
  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    if allBodyRegionsArmIncluded:
      pickle.dump({'Knee': [maxStressScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, stressMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee], 'Arm': [maxStressScoresArm, totDaysAscendingPainArm, totDaysDescendingPainArm, dataArm, data2Arm, stressMinMaxAmplitudesArm, painMinMaxAmplitudesArm], 'Head': [maxStressScoresHead, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, stressMinMaxAmplitudesHead, painMinMaxAmplitudesHead]}, output)
    else:
      pickle.dump({'Knee': [maxStressScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, stressMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee], 'Head': [maxStressScoresHead, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, stressMinMaxAmplitudesHead, painMinMaxAmplitudesHead]}, output)
    output.close()
  
  nbAscendingDays  = totDaysAscendingPainKnee + totDaysAscendingPainHead
  nbDescendingDays = totDaysDescendingPainKnee + totDaysDescendingPainHead
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxStressScores >= 0, maxStressScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxStressScores <= 0, maxStressScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [(nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays), nbAscendingDays + nbDescendingDays, regScore, nbAscendingDays, nbDescendingDays]


def calculateForAllRegionsParticipant2(data, parameters, plotGraphs, saveData=False):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']

  # Knee plots
  [maxStressScoresKnee, maxStressScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, stressMinMaxAmplitudes, painMinMaxAmplitudes] = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(data, "kneepain", ["steps", "denivelation"], [1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph)

  maxStressScores = maxStressScoresKnee
  if plotGraphs:
    plt.hist(maxStressScores)
    plt.show()

  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    pickle.dump({'Knee': [maxStressScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee]}, output)
    output.close()
  
  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxStressScores >= 0, maxStressScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxStressScores <= 0, maxStressScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [(nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays), nbAscendingDays + nbDescendingDays]


def calculateForAllRegionsParticipant8(data, parameters, plotGraphs, saveData=False):

  rollingMeanWindow = parameters['rollingMeanWindow']
  rollingMinMaxScalerWindow = parameters['rollingMinMaxScalerWindow']
  rollingMedianWindow = parameters['rollingMedianWindow']
  minProminenceForPeakDetect = parameters['minProminenceForPeakDetect']
  windowForLocalPeakMinMaxFind = parameters['windowForLocalPeakMinMaxFind']
  plotGraph = parameters['plotGraph']

  # Knee plots
  [maxStressScoresKnee, maxStressScores2Knee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, stressMinMaxAmplitudes, painMinMaxAmplitudes] = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(data, "kneepain", ["steps"], [1], rollingMeanWindow, rollingMinMaxScalerWindow, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph)

  maxStressScores = maxStressScoresKnee
  if plotGraphs:
    plt.hist(maxStressScores, range=(-1, 1))
    plt.show()

  # Saving data
  if saveData:
    output = open("peaksData.txt", "wb")
    pickle.dump({'Knee': [maxStressScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee]}, output)
    output.close()
  
  nbAscendingDays  = totDaysAscendingPainKnee
  nbDescendingDays = totDaysDescendingPainKnee
  
  extendingAscendingNbDays  = nbAscendingDays + 0.2 * nbDescendingDays
  extendingDescendingNbDays = 0.8 * nbDescendingDays
  
  nbPointsInAscendingDays  = np.sum(np.logical_or(maxStressScores >= 0, maxStressScores <= -0.8))
  nbPointsInDescendingDays = np.sum(np.logical_and(maxStressScores <= 0, maxStressScores >= -0.8))
  
  if False:
    print("nbPointsInAscendingDays:", nbPointsInAscendingDays, "; nbPointsInDescendingDays:", nbPointsInDescendingDays)
    print("extendingAscendingNbDays:", extendingAscendingNbDays, "; extendingDescendingNbDays:", extendingDescendingNbDays)
    print("rapport: ", (nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays))
  
  return [(nbPointsInAscendingDays / extendingAscendingNbDays) / (nbPointsInDescendingDays / extendingDescendingNbDays), nbAscendingDays + nbDescendingDays]
