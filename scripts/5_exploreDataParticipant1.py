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


def visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(region, list_of_stressors, stressor_coef, window, window2, plotShift):
  
  fig, axes = plt.subplots(nrows=5, ncols=1)
  fig.suptitle(region, fontsize=8)
  scaler = MinMaxScaler()
  
  # Plotting potential stressors causing pain in region

  data[list_of_stressors] = scaler.fit_transform(data[list_of_stressors])
  data[list_of_stressors].plot(ax=axes[0], linestyle='', marker='o', markersize=0.5)
  axes[0].legend(loc='upper right', prop={'size': 5})
  axes[0].title.set_text('Stressors causing ' + region)
  axes[0].title.set_fontsize(5)
  axes[0].title.set_position([0.5, 0.93])
  axes[0].get_xaxis().set_visible(False)

  # Plotting stress and pain
  
  stress_and_pain = ["regionSpecificStress", region]
  data["regionSpecificStress"] = np.zeros(len(data[list_of_stressors[0]]))
  for idx, stressor in enumerate(list_of_stressors):
    data["regionSpecificStress"] = data["regionSpecificStress"] + stressor_coef[idx] * data[stressor]
  data[stress_and_pain] = scaler.fit_transform(data[stress_and_pain])
  data[stress_and_pain].plot(ax=axes[1], linestyle='', marker='o', markersize=0.5)
  axes[1].legend(('stress', 'pain'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[1].title.set_text('Combined Stress (linear combination of previous stressors) and pain')
  axes[1].title.set_fontsize(5)
  axes[1].title.set_position([0.5, 0.93])
  axes[1].get_xaxis().set_visible(False)

  # Plotting Rolling Mean of stress and pain
  
  for var in stress_and_pain:
    data[var + "_RollingMean"] = data[var].rolling(window).mean()
  stress_and_pain_rollingMean = [name + "_RollingMean" for name in stress_and_pain]
  data[stress_and_pain_rollingMean].plot(ax=axes[2])
  axes[2].legend(('stress', 'pain'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[2].title.set_text('Rolling mean of combined stress and pain')
  axes[2].title.set_fontsize(5)
  axes[2].title.set_position([0.5, 0.93])
  axes[2].get_xaxis().set_visible(False)
  
  # Plotting Rolling MinMaxScaler of Rolling Mean of stress and pain

  stress_and_pain_RollingMean_MinMaxScaler = [name + "_MinMaxScaler" for name in stress_and_pain_rollingMean]
  for columnName in stress_and_pain_rollingMean:
    data[columnName + "_MinMaxScaler"] = rollingMinMaxScaler(data, columnName, window2) #.rolling(window).mean()
  data[stress_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[3])
  axes[3].legend(('stress', 'pain'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[3].title.set_text('Rolling MinMaxScaler of rolling mean of combined stress and pain')
  axes[3].title.set_fontsize(5)
  axes[3].title.set_position([0.5, 0.93])
  axes[3].get_xaxis().set_visible(False)
  
  # Calculating optimal shift on stress
  
  [optimalStressPainShift, diffValsX, diffVals] = findOptimalStressShiftForPain(data.copy(), stress_and_pain_RollingMean_MinMaxScaler[1])
  print("optimalStressPainShift for ", region, ":", optimalStressPainShift)
  
  # Plotting Rolling MinMaxScaler of Rolling Mean of stress and pain with shift on stress  
  
  data[stress_and_pain_RollingMean_MinMaxScaler[0]] = data[stress_and_pain_RollingMean_MinMaxScaler[0]].shift(periods = optimalStressPainShift)
  data[stress_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[4])
  
  axes[4].legend(('stress', 'pain'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[4].title.set_text('Rolling MinMaxScaler of rolling mean of combined stress and pain, with time shift of ' + str(optimalStressPainShift) + ' days on stress (time shift calculated automatically)')
  axes[4].title.set_fontsize(5)
  axes[4].title.set_position([0.5, 0.93])
  
  # Showing the final plot

  plt.show()
  
  if plotShift:
    fig, axes = plt.subplots(nrows=1, ncols=1)
    plt.plot(diffValsX, diffVals)
    plt.show()
    
  return data[stress_and_pain_RollingMean_MinMaxScaler]


# Getting data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

rollingMeanWindow         = 21
rollingMinMaxScalerWindow = 50
plotShift                 = False

# Knee Plots
knee = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("kneePain", ["tracker_mean_distance", "tracker_mean_denivelation", "timeDrivingCar", "swimmingKm", "cycling"], [1, 1, 0.15, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, plotShift)

# Finger Hand Arm Plots
handArm = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("fingerHandArmPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata"], [1, 1, 2, 1, 1, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, plotShift)

# Forehead Eyes Plots
aroundEyes = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("foreheadEyesPain", ["manicTimeDelta_corrected", "timeDrivingCar"], [1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, plotShift)

