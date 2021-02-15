# The previous scripts show a correlation between exercise and pain for Participant 1.

# This script goes a step further: it identifies "long periods of high pain intensity" and allows to visualize which factors may have cause these long pain periods to start.

# After visualizing the graphs, it looks like some of these "long periods of high pain intensity" may be caused by:
# - high stress just before the beginning of the long pain period (or a few days (maybe up to a week) before)
# - gradual increase (over a long time period (two weeks / one month)) in stress leading to a "build-up" in stress before the beginning of the long pain period
# - decrease in general mood just before the long pain period
# - decrease in maximum pain in other regions before the beginning of the long pain period (leaving some "room" for the pain in the particular region to "show up")
# - an "unusual" activity is introduced before the beginning of the long pain period

# However, looking at the graphs, it isn't always clear what these pain periods are caused by. Also something to be aware of is that sometimes the tracker was not worn by Participant 1 (because he forgot it, the battery died, etc..). It looks like this sometimes happened before the beginning of a long pain period. It's also possible that looking at the distance and/or the number of calories burnt (instead of the number of steps taken) might be better.

# Next tasks ToDo for Olivier (he will need to look into his notes and other data sources for this):
# - replace the number of steps taken by the distance walked and calories burned in the analysis
# - find when the tracker was not worn and to try estimate the number of steps/distance walked that was missed
# - try to find when "unusual" activities where performed and have a quantification of this

# Next task for anyone who wants to look into it:
# - try to find good predictors of the "long periods of high pain intensity" occurences


import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values, rollingMinMaxScaler


def findOptimalStressShiftForPain(data, painRegName):
  
  diffVals  = []
  diffValsX = []
  
  for i in range(0, 120):
    diff = (data[painRegName] - data["regionSpecificStress_RollingMean_MinMaxScaler"]).tolist() # pain - stress
    diff = [x if data[painRegName][idx] >= 0.8 else float('nan') for idx, x in enumerate(diff)]
    diff = [x for x in diff if str(x) != 'nan']
    diff = [d if d >=0 else 0 for d in diff]
    diffSum = np.sum(diff) / len(diff)
    diffVals.append(diffSum)
    diffValsX.append(i)
    data["regionSpecificStress_RollingMean_MinMaxScaler"] = data["regionSpecificStress_RollingMean_MinMaxScaler"].shift(periods = 1)
  
  shift = np.argmin(diffVals)
    
  return [shift, diffValsX, diffVals]


def visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(region, list_of_stressors, stressor_coef, window, window2, list_of_stressors2):
  
  fig, axes = plt.subplots(nrows=4, ncols=1)
  fig.suptitle(region, fontsize=8)
  scaler = MinMaxScaler()
  
  # Subplot 1: Plotting potential stressors causing pain in region

  data[list_of_stressors] = scaler.fit_transform(data[list_of_stressors])
  data[list_of_stressors].plot(ax=axes[0], linestyle='', marker='o', markersize=0.5)

  # Subplot 2: Combined Stress (linear combination of previous stressors) and pain
  
  stress_and_pain = ["regionSpecificStress", region]
  data["regionSpecificStress"] = np.zeros(len(data[list_of_stressors[0]]))
  for idx, stressor in enumerate(list_of_stressors):
    data["regionSpecificStress"] = data["regionSpecificStress"] + stressor_coef[idx] * data[stressor]
  data[stress_and_pain] = scaler.fit_transform(data[stress_and_pain])
  data[stress_and_pain].plot(ax=axes[1], linestyle='', marker='o', markersize=0.5)

  # Subplot 3 : Identifying long pain periods starting points + Stress today and yesterday compared to mean value in the last 3 weeks
  
  data["regionSpecificPainBinary"] = data[region].copy()
  
  for i in range(0, 275):
    if data["regionSpecificPainBinary"][i] > 0.85:
      data["regionSpecificPainBinary"][i] = 1
    else:
      data["regionSpecificPainBinary"][i] = 0 
  for i in range(275, 459):
    if data["regionSpecificPainBinary"][i] > 0.75:
      data["regionSpecificPainBinary"][i] = 1
    else:
      data["regionSpecificPainBinary"][i] = 0       
  for i in range(459, len(data[region])):
    if data["regionSpecificPainBinary"][i] > 0.5:
      data["regionSpecificPainBinary"][i] = 1
    else:
      data["regionSpecificPainBinary"][i] = 0
  
  data["regionSpecificPainBinary2"] = data["regionSpecificPainBinary"].copy()
  for i in range(0, 2):
    data["regionSpecificPainBinary2"][i] = 0
  for i in range(len(data["regionSpecificPainBinary2"]-2), len(data["regionSpecificPainBinary2"])):
    data["regionSpecificPainBinary2"][i] = 0
  for i in range(2, len(data["regionSpecificPainBinary2"])-2):
    if (data["regionSpecificPainBinary2"][i-1] == 1 and data["regionSpecificPainBinary2"][i+1] == 1) or (data["regionSpecificPainBinary2"][i-2] == 1 and data["regionSpecificPainBinary2"][i+1] == 1) or (data["regionSpecificPainBinary2"][i-1] == 1 and data["regionSpecificPainBinary2"][i+2] == 1):
      data["regionSpecificPainBinary2"][i] = 1
  for i in range(2, len(data["regionSpecificPainBinary2"])-2):
    if data["regionSpecificPainBinary2"][i-1] == 0 and data["regionSpecificPainBinary2"][i+1] == 0:
      data["regionSpecificPainBinary2"][i] = 0
  data["regionSpecificPainBinary2"] = data["regionSpecificPainBinary2"].replace(1, 0.9)
  
  data["regionSpecificPainBinary"].plot(ax=axes[2], linestyle='', marker='o', markersize=0.5)
  data["regionSpecificPainBinary2"].plot(ax=axes[2], linestyle='', marker='o', markersize=0.5)
  
  data["regionSpecificPainStart"] = data["regionSpecificPainBinary2"].copy()
  data["regionSpecificPainStart"][0] = 0
  for i in range(1, len(data["regionSpecificPainBinary2"])-2):
    if (data["regionSpecificPainBinary2"][i-1] == 0) and (data["regionSpecificPainBinary2"][i] == 0.9) and (data["regionSpecificPainBinary2"][i+1] == 0.9) and (data["regionSpecificPainBinary2"][i+2] == 0.9):
      data["regionSpecificPainStart"][i] = 1.1
    else:
      data["regionSpecificPainStart"][i] = 0
  
  stressBuildUpFirstCheck         = 6
  stressBuildUpSecondCheck        = 12
  specStressHigherReferencePeriod = 5*7 #21
  longReferencePeriod             = 5*7
  data["regionSpecificStressBuildUp"] = data["regionSpecificStress"].copy()
  data["regionSpecificStressHigher"]  = data["regionSpecificStress"].copy()
  for i in range(longReferencePeriod, len(data["regionSpecificStress"])):
    data["regionSpecificStressBuildUp"][i]     = (np.mean(data["regionSpecificStress"][i-stressBuildUpFirstCheck:i]) - np.mean(data["regionSpecificStress"][i-stressBuildUpSecondCheck:i-stressBuildUpFirstCheck])) / np.mean(data["regionSpecificStress"][i-longReferencePeriod:i])
    data["regionSpecificStressHigher"][i] = np.maximum((data["regionSpecificStress"][i] - np.mean(data["regionSpecificStress"][i-specStressHigherReferencePeriod:i])) / np.mean(data["regionSpecificStress"][i-longReferencePeriod:i]), (data["regionSpecificStress"][i-1] - np.mean(data["regionSpecificStress"][i-specStressHigherReferencePeriod:i])) / np.mean(data["regionSpecificStress"][i-longReferencePeriod:i]))
  for i in range(0, longReferencePeriod):
    data["regionSpecificStressBuildUp"][i] = data["regionSpecificStressBuildUp"][longReferencePeriod]
    data["regionSpecificStressHigher"][i]  = data["regionSpecificStressHigher"][longReferencePeriod]
  
  maxx = np.max(data["regionSpecificStressHigher"])
  data["regionSpecificStressHigher"] = data["regionSpecificStressHigher"] / maxx
  
  data["regionSpecificStressHigher"].plot(ax=axes[2], linestyle='', marker='o', markersize=0.5)
  
  # Subplot 4: Plotting other factors that might be influencing pain
  
  data["maxPain"] = data["fingerHandArmPain"].copy()
  for i in range(0, len(data["fingerHandArmPain"])):
    if region == "kneePain":
      data["maxPain"][i] = np.max([data["fingerHandArmPain"][i], data["shoulderNeckPain"][i], data["foreheadEyesPain"][i], data["sick_tired"][i]])
    elif region == "fingerHandArmPain":
      data["maxPain"][i] = np.max([data["kneePain"][i], data["shoulderNeckPain"][i], data["foreheadEyesPain"][i], data["sick_tired"][i]])
    elif region == "foreheadEyesPain":
      data["maxPain"][i] = np.max([data["fingerHandArmPain"][i], data["shoulderNeckPain"][i], data["kneePain"][i], data["sick_tired"][i]])
  
  data[list_of_stressors2] = scaler.fit_transform(data[list_of_stressors2])
  data[list_of_stressors2].plot(ax=axes[3], linestyle='', marker='o', markersize=0.5)
  data["regionSpecificPainStart"].plot(ax=axes[3], linestyle='', marker='o', markersize=2)
  data["regionSpecificPainStart"].plot(ax=axes[0], linestyle='', marker='o', markersize=2)
  data["regionSpecificPainStart"].plot(ax=axes[1], linestyle='', marker='o', markersize=2)
  data["regionSpecificPainStart"].plot(ax=axes[2], linestyle='', marker='o', markersize=2)
  
  # Axes of plots
  
  axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 5})
  axes[0].title.set_text('Main stressors that might be causing ' + region)
  axes[0].title.set_fontsize(5)
  axes[0].title.set_position([0.5, 0.93])
  axes[0].get_xaxis().set_visible(False)
  
  axes[1].legend(('stress', 'pain'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[1].title.set_text('Combined Stress (linear combination of previous stressors) and pain')
  axes[1].title.set_fontsize(5)
  axes[1].title.set_position([0.5, 0.93])
  axes[1].get_xaxis().set_visible(False)
  
  axes[2].legend(('painOverThresh', 'painOverThreshMed', 'curStressCompLast3Weeks', 'longPainPeriodStart'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[2].title.set_text('Identifying long pain periods starting points ("top" points (above 0.9)) + Stress today and yesterday compared to mean value in the last 3 weeks ("bottom" point (below 0.9))')
  axes[2].title.set_fontsize(5)
  axes[2].title.set_position([0.5, 0.93])
  axes[2].get_xaxis().set_visible(False)
  
  axes[3].legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 5})
  axes[3].title.set_text('Other factors that might be influencing pain')
  axes[3].title.set_fontsize(5)
  axes[3].title.set_position([0.5, 0.93])
  axes[3].get_xaxis().set_visible(False)
  
  # Showing the final plot

  plt.show()
    
  return data


# Getting data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

rollingMeanWindow         = 21
rollingMinMaxScalerWindow = 50

# Knee Plots
knee = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("kneePain", ["tracker_mean_distance", "tracker_mean_denivelation", "timeDrivingCar", "swimmingKm", "cycling"], [1, 1, 0.15, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["climbingDenivelation", "viaFerrata", "generalmood", "manicTimeDelta_corrected", "maxPain"])

# Finger Hand Arm Plots
handArm = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("fingerHandArmPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata", "scooterRiding"], [1, 1, 2, 1, 1, 1, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["generalmood", "maxPain"])

# Forehead Eyes Plots
aroundEyes = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("foreheadEyesPain", ["manicTimeDelta_corrected", "timeDrivingCar"], [1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["generalmood", "maxPain"])

