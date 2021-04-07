import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values, rollingMinMaxScaler
from scipy import stats

def relativeValuePercentile(data, fieldToProcess, newFieldName, targetRegion, referenceRegion):
  targetRegion    = [val - 1 for val in targetRegion]
  referenceRegion = [val - 1 for val in referenceRegion]
  startCalculation   = max(targetRegion[1], referenceRegion[1])
  data[newFieldName] = data[fieldToProcess].copy()
  for i in range(startCalculation, len(data[fieldToProcess])):
    value     = np.mean(data[fieldToProcess][i-targetRegion[1]:i-targetRegion[0]])
    reference = data[fieldToProcess][i-referenceRegion[1]:i-referenceRegion[0]]
    data[newFieldName][i] = stats.percentileofscore(reference.tolist(), value)
  for i in range(0, startCalculation):
    data[newFieldName][i] = data[newFieldName][startCalculation]
  return data

def searchForWarningSigns(data, region, list_of_stressors, stressor_coef, list_of_stressors2, specialTreatmentStressor, quantilePeriodForCompare, highPainPeriodStartsManualStart):
  
  scaler = MinMaxScaler()
  
  # regionSpecificPainStart
  
  data["regionSpecificPainStart"] = data[region].copy()
  data["regionSpecificPainStart"][0] = 0
  for i in range(0, len(data["regionSpecificPainStart"])):
    periodStart = False
    for date in highPainPeriodStartsManualStart:
      if date == data["regionSpecificPainStart"].index[i].strftime("%d/%m/%Y"):
        periodStart = True
    if periodStart:
      data["regionSpecificPainStart"][i] = 1.1
    else:
      data["regionSpecificPainStart"][i] = 0
  
  # Preparing first figure
  
  fig, axes = plt.subplots(nrows=5, ncols=1)
  fig.suptitle(region, fontsize=8)
  
  # Subplot 0: Plotting potential stressors causing pain in region

  data[list_of_stressors] = scaler.fit_transform(data[list_of_stressors])
  data[list_of_stressors].plot(ax=axes[0], linestyle='', marker='o', markersize=0.5)

  # Subplot 1: Combined Stress (linear combination of previous stressors) and pain
  
  stress_and_pain = ["regionSpecificStress", region]
  data["regionSpecificStress"] = np.zeros(len(data[list_of_stressors[0]]))
  for idx, stressor in enumerate(list_of_stressors):
    data["regionSpecificStress"] = data["regionSpecificStress"] + stressor_coef[idx] * data[stressor]
  data[stress_and_pain] = scaler.fit_transform(data[stress_and_pain])
  data[stress_and_pain].plot(ax=axes[1], linestyle='', marker='o', markersize=0.5)

  # Subplot 2 and 3 : Calculating relative values for pain, combined stress, and one arbitrarly chosen stressor
  
  data = relativeValuePercentile(data, region, "relativePain", [0, 1], [0, 150])
  
  data = relativeValuePercentile(data, "regionSpecificStress", "relativeStress", [0, 12], [12, 90])
  
  if specialTreatmentStressor:
    all = ["relativePain", specialTreatmentStressor]
    data[all] = scaler.fit_transform(data[all])
    data[all].plot(ax=axes[2], linestyle='', marker='o', markersize=0.5)

  all = ["relativePain", "relativeStress"]
  data[all] = scaler.fit_transform(data[all])
  data[all].plot(ax=axes[3], linestyle='', marker='o', markersize=0.5)
  
  # Subplot 4: Finding when a warning sign should be raised
  # Warning signs calculations are based exclusevily on NON-pain values for the present and previous days
  
  data["warningSign"] = data[region].copy()
  data["warningSign"][0] = 0
  for i in range(0, 180):
    data["warningSign"][i] = 0
    
  countPositiveWarningSign = 0
  warningSignStartDay = 180
  for i in range(warningSignStartDay, len(data["warningSign"])):
    if i > quantilePeriodForCompare:
      timePeriod = quantilePeriodForCompare
    else:
      timePeriod = i
    if specialTreatmentStressor:
      specialTreatmentStressorThreshold = np.quantile(data[specialTreatmentStressor][i-timePeriod:i-12], 0.98)
    stressThreshold = np.quantile(data["relativeStress"][i-timePeriod:i-12], 0.98)
    if data["relativeStress"][i] > stressThreshold:
      data["warningSign"][i] = 1.2
      countPositiveWarningSign = countPositiveWarningSign + 1
    else:
      if specialTreatmentStressor:
        if data[specialTreatmentStressor][i] > specialTreatmentStressorThreshold or data[specialTreatmentStressor][i-1] > specialTreatmentStressorThreshold:
          data["warningSign"][i] = 1.3
          countPositiveWarningSign = countPositiveWarningSign + 1
        else:
          data["warningSign"][i] = 0
      else:
        data["warningSign"][i] = 0
  
  print("Percentage of warnings raised:", countPositiveWarningSign/(len(data[region])-warningSignStartDay)*100, "%, ", "(", countPositiveWarningSign, "out of", len(data[region])-warningSignStartDay, ")")
  
  data[["relativePain", "warningSign"]].plot(ax=axes[4], linestyle='', marker='o', markersize=0.5)
  
  # Preparing and showing the final plots for the first figure
  
  for i in range(0, 5):
    data["regionSpecificPainStart"].plot(ax=axes[i], linestyle='', marker='o', markersize=2)
    axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 5})
    # axes[i].title.set_text('description here')
    axes[i].title.set_fontsize(5)
    axes[i].title.set_position([0.5, 0.93])
    axes[i].get_xaxis().set_visible(False)
  plt.show()
  
  # Second summary Plot
  
  if True:
    fig, axes = plt.subplots(nrows=2, ncols=1)
    fig.suptitle(region, fontsize=8)
    data[[region]].plot(ax=axes[0], linestyle='', marker='o', markersize=0.5)
    data[["relativePain", "warningSign"]].plot(ax=axes[1], linestyle='', marker='o', markersize=0.5)
    for i in range(0, 2):
      data["regionSpecificPainStart"].plot(ax=axes[i], linestyle='', marker='o', color='k', markersize=2)
      axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 5})
      # axes[i].title.set_text('description here')
      axes[i].title.set_fontsize(5)
      axes[i].title.set_position([0.5, 0.93])
      axes[i].get_xaxis().set_visible(False)
    plt.show()
  
  return data


# Getting data
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Forehead Eyes Plots
aroundEyes = searchForWarningSigns(data, "foreheadEyesPain", ["manicTimeDelta_corrected", "timeDrivingCar"], [1, 1], ["generalmood", "maxPain"], "timeDrivingCar", 200, ["24/07/2016","08/09/2016", "20/05/2017", "09/06/2018", "12/07/2018", "19/06/2019", "05/04/2020"])

# Knee Plots
knee = searchForWarningSigns(data, "kneePain", ["tracker_mean_distance", "tracker_mean_denivelation", "timeDrivingCar", "swimmingKm", "cycling"], [1, 1, 0.15, 0.2, 0.3], ["climbingDenivelation", "viaFerrata", "generalmood", "manicTimeDelta_corrected", "maxPain"], "", 60, ["18/02/2016", "19/03/2016", "11/08/2016", "17/10/2016", "13/08/2017", "12/11/2017", "09/05/2018", "05/08/2018", "15/10/2018", "15/10/2020"])


