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


def visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain(region, list_of_stressors, stressor_coef, window, window2, list_of_stressors2, highPainPeriodStarts):
  
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

  # Subplot 3 : Rolling mean of combined stress and pain
  
  for var in stress_and_pain:
    data[var + "_RollingMean"] = data[var].rolling(window).mean()
  stress_and_pain_rollingMean = [name + "_RollingMean" for name in stress_and_pain]
  data[stress_and_pain_rollingMean] = scaler.fit_transform(data[stress_and_pain_rollingMean])
  data[stress_and_pain_rollingMean].plot(ax=axes[2])
  
  data["regionSpecificPainStart"] = data[region].copy()
  data["regionSpecificPainStart"][0] = 0
  for i in range(1, len(data["regionSpecificPainStart"])-2):
    periodStart = False
    for date in highPainPeriodStarts:
      if date == data["regionSpecificPainStart"].index[i].strftime("%d/%m/%Y"):
        periodStart = True
    if periodStart:
      data["regionSpecificPainStart"][i] = 1.1
    else:
      data["regionSpecificPainStart"][i] = 0
  
  # Subplot 4: Plotting other factors that might be influencing pain
  
  allRegions = ["kneePain", "foreheadEyesPain", "handsAndFingerPain", "forearmElbowPain", "shoulderNeckPain", "sick_tired", "painInOtherRegion"]
  allRegions.remove(region)
  
  data["maxPain"] = data["fingerHandArmPain"].copy()
  for i in range(0, len(data["fingerHandArmPain"])):   
    data["maxPain"][i] = np.max([data[otherRegion][i] for otherRegion in allRegions])
  
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
  
  axes[1].legend(('stress', 'pain', 'longPainPeriodStart'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[1].title.set_text('Combined Stress (linear combination of previous stressors) and pain')
  axes[1].title.set_fontsize(5)
  axes[1].title.set_position([0.5, 0.93])
  axes[1].get_xaxis().set_visible(False)
  
  axes[2].legend(('stress', 'pain', 'longPainPeriodStart'), loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
  axes[2].title.set_text('Rolling mean of combined stress and pain')
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
knee = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("kneePain", ["tracker_mean_distance", "tracker_mean_denivelation", "timeDrivingCar", "swimmingKm", "cycling"], [1, 1, 0.15, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["climbingDenivelation", "viaFerrata", "generalmood", "manicTimeDelta_corrected", "maxPain"], ["18/02/2016", "19/03/2016", "11/08/2016", "17/10/2016", "13/08/2017", "12/11/2017", "09/05/2018", "05/08/2018", "15/10/2018", "15/10/2020"])

# Forehead Eyes Plots
aroundEyes = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("foreheadEyesPain", ["manicTimeDelta_corrected", "timeDrivingCar"], [1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["generalmood", "maxPain"], ["24/07/2016","08/09/2016", "20/05/2017", "09/06/2018", "12/07/2018", "19/06/2019", "05/04/2020"])

# Shoulder Neck Plots
handArm = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("shoulderNeckPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata", "scooterRiding"], [1, 1, 2, 1, 1, 1, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["generalmood", "maxPain"], ["05/07/2017", "06/10/2017", "09/06/2018", "27/03/2020", "25/05/2020", "10/07/2020", "04/09/2020", "04/11/2020"])

# Hands and Finger Plots
handArm = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("handsAndFingerPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata", "scooterRiding"], [1, 1, 2, 1, 1, 1, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["generalmood", "maxPain"], ["03/04/2016", "29/09/2016", "03/02/2017", "27/08/2017", "11/12/2017", "18/08/2018", "08/01/2019", "14/09/2019", "21/12/2019", "12/04/2020", "30/06/2020", "02/11/2020"])

# Forearm Elbow Plots
handArm = visualizeRollingMinMaxScalerofRollingMeanOfStressAndPain("forearmElbowPain", ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata", "scooterRiding"], [1, 1, 2, 1, 1, 1, 1, 1], rollingMeanWindow, rollingMinMaxScalerWindow, ["generalmood", "maxPain"], ["20/02/2016", "18/08/2016", "02/04/2017", "01/10/2017", "21/09/2018", "11/10/2019", "01/02/2020", "11/07/2020", "02/11/2020"])

