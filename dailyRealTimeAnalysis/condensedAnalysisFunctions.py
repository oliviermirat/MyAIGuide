import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np

scaler = MinMaxScaler()

def addEmptyFieldForActivites(monitoring_hr, heart_rate_active_threshold, activityList):
  for activity in activityList:
    monitoring_hr["act_hr_" + str(heart_rate_active_threshold) + "_" + activity + "_lowBody"] = 0
    monitoring_hr["act_hr_" + str(heart_rate_active_threshold) + "_" + activity + "_highBody"] = 0
  return monitoring_hr

def addDataForActivities(monitoring_hr, selectedTime, heart_rate_active_threshold, activityList, coeff, keyToCoeff, currentActivity):
  for activity in activityList:
    if activity == currentActivity:
      monitoring_hr.loc[selectedTime, "act_hr_" + str(heart_rate_active_threshold) + "_" + activity + "_lowBody"] = coeff[keyToCoeff[activity]]['low_body'] * monitoring_hr.loc[selectedTime, 'active_hr_' + str(heart_rate_active_threshold)]
      monitoring_hr.loc[selectedTime, "act_hr_" + str(heart_rate_active_threshold) + "_" + activity + "_highBody"] = coeff[keyToCoeff[activity]]['high_body'] * monitoring_hr.loc[selectedTime, 'active_hr_' + str(heart_rate_active_threshold)]
  return monitoring_hr

def returnMonitoring_hr_Variables(activityList, heart_rate_active_threshold):
  allVariables = []
  for activity in activityList:
    allVariables += ["act_hr_" + str(heart_rate_active_threshold) + "_" + activity + "_" + bodyRegion for bodyRegion in ["lowBody", "highBody"]]
  return allVariables

def plotAdditionalActivitiesAnalysis(data, heart_rate_active_threshold_values, activityList, rollingWindow, figWidth, figHeight, hspace, lineWidth):
  
  scaler = MinMaxScaler()
  
  data["act_lowBody"] = data['act_hr_' + str(heart_rate_active_threshold_values[0]) + '_lowBody'] + data['act_hr_' + str(heart_rate_active_threshold_values[1]) + '_lowBody']
  
  a = []
  for heart_rate_active_threshold in heart_rate_active_threshold_values:
    a += returnMonitoring_hr_Variables(activityList, heart_rate_active_threshold)
  
  listOfVariables = ['realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain'] + np.array([['active_hr_' + str(heart_rate_active_threshold), 'act_hr_' + str(heart_rate_active_threshold) + '_lowBody', 'act_hr_' + str(heart_rate_active_threshold) + '_highBody'] for heart_rate_active_threshold in heart_rate_active_threshold_values]).flatten().tolist() + a + ['garminSteps', 'garminCyclingActiveCalories',  'realTimeEyeDrivingTime', 'realTimeEyeRidingTime', 'whatPulseRealTime', 'manicTimeRealTime', 'realTimeEyeInCar', 'computerAndCarRealTime', 'climbingDenivelation', 'climbingMaxEffortIntensity', 'garminClimbingActiveCalories', 'garminKneeRelatedActiveCalories', 'swimSurfStrokes', 'act_lowBody']


  listOfVariables_scaled = [var + 'sca' for var in listOfVariables]

  data[listOfVariables_scaled] = scaler.fit_transform(data[listOfVariables])

  # Rolling mean plotting

  for variable in listOfVariables:
    data[variable + "_RollingMean"] = data[variable].rolling(rollingWindow).mean()

  data[[var + "_RollingMean" for var in listOfVariables]] = scaler.fit_transform(data[[var + "_RollingMean" for var in listOfVariables]])


  # OtherActivities

  # lowBodyVars1 = ['act_lowBody', 'garminKneeRelatedActiveCalories', 'realTimeKneePain']
  lowBodyVars1 = ['garminKneeRelatedActiveCalories', 'garminSteps', 'realTimeKneePain']
  lowBodyVars2 = ['act_hr_' + str(heart_rate_active_threshold_values[1]) + "_cycling_lowBody", 'realTimeKneePain']
  lowBodyVars3 = ['manicTimeRealTime', 'realTimeKneePain']
  # colors_lowBodyVars1 = ['blue', 'orange', 'red']
  colors_lowBodyVars1 = ['black', 'green', 'red']
  colors_lowBodyVars2 = ['purple', 'red']
  colors_lowBodyVars3 = ['black', 'red']
  # labels1 = ['calOli', 'calGar', 'knee']
  labels1 = ['kneeCal', 'step', 'knee']
  labels2 = ['cycleCal', 'knee']
  labels3 = ['computer', 'knee']

  fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=3, ncols=1)
  fig.subplots_adjust(left=0.05, bottom=0.01, right=0.98, top=0.95, wspace=None, hspace=hspace)
  # data[[var + "_RollingMean" for var in lowBodyVars1]].plot(ax=axes[0], color=colors_lowBodyVars1, label=labels1)
  for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars1], colors_lowBodyVars1, labels1):
    data[col].plot(ax=axes[0], color=color, label=label, linewidth=lineWidth)
  # axes[0].legend(loc='upper left')
  # data[[var + "_RollingMean" for var in lowBodyVars2]].plot(ax=axes[1], color=colors_lowBodyVars2, label=labels2)
  for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars2], colors_lowBodyVars2, labels2):
    data[col].plot(ax=axes[1], color=color, label=label, linewidth=lineWidth)
  # axes[1].legend(loc='upper left')
  # data[[var + "_RollingMean" for var in lowBodyVars3]].plot(ax=axes[2], color=colors_lowBodyVars3, label=labels3)
  for col, color, label in zip([var + "_RollingMean" for var in lowBodyVars3], colors_lowBodyVars3, labels3):
    data[col].plot(ax=axes[2], color=color, label=label, linewidth=lineWidth)
  # axes[2].legend(loc='upper left')
  # plt.savefig('11_' + parameterOption['figName'] + '_a_low.' + figsFormat, format=figsFormat)
  plt.show()
