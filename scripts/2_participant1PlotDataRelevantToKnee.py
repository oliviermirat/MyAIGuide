# This scripts assumes that the dataframe has been created and saved in data.txt

import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values
from sklearn.preprocessing import MinMaxScaler

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Removing "steps" caused by scooter riding
data["fitbitSteps"] = data["fitbitSteps"] - 37 * data["scooterRiding"]
data["fitbitSteps"][data["fitbitSteps"] < 0] = 0

# Selecting the different periods where different trackers where used
period1 = ("2015-12-26", "2016-06-21")  # basis and googlefit
period2 = ("2016-06-22", "2016-09-01")  # basis
period3 = ("2016-09-02", "2017-01-01")  # basis and fitbit
period4 = ("2017-01-02", "2017-10-16")  # fitbit
period5 = ("2017-10-17", "2018-07-02")  # fitbit and moves
period6 = ("2018-07-03", "2018-07-30")  # fitbit and moves and googlefit
period7 = ("2018-07-31", "2020-02-01")  # fitbit and googlefit

# Creating the tracker_mean_steps variable in the dataframe
# and puts harmonized steps value inside
data["tracker_mean_distance"] = data["fitbitDistance"]
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period3, data, "basisPeakSteps", "fitbitDistance", "tracker_mean_distance")
data = predict_values(period1, data, "basisPeakSteps", "tracker_mean_distance", reg)
data = predict_values(period2, data, "basisPeakSteps", "tracker_mean_distance", reg)
data = insert_data_to_tracker_mean_steps(period4, data, "fitbitDistance", "tracker_mean_distance")
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period5, data, "movesSteps", "fitbitDistance", "tracker_mean_distance")
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period6, data, "movesSteps", "fitbitDistance", "tracker_mean_distance")
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period7, data, "googlefitSteps", "fitbitDistance", "tracker_mean_distance")

# Creating the tracker_mean_denivelation variable in the dataframe
# and puts harmonized denivelation value inside
data["elevation_gain"] = data["elevation_gain"] * (300/14000)
data["cum_gain"] = data["cum_gain_walking"].fillna(0) + data["cum_gain_cycling"].fillna(0) + data["cum_gain_running"].fillna(0)
data["cum_gain"] = data["cum_gain"] * (300/1000)
outlierThreshold = 4
z = np.abs(stats.zscore(data["elevation_gain"]))
print("Number of outliers detected for Google fit based elevation gain:", len(np.where(z > outlierThreshold)[0]))
for outlier in np.where(z > outlierThreshold):
  print("1:", outlier)
  data["elevation_gain"][outlier] = data["elevation_gain"][outlier] / 3
z = np.abs(stats.zscore(data["cum_gain"]))
np.where(z > outlierThreshold)
print("Number of outliers detected for Moves app based elevation gain:", len(np.where(z > outlierThreshold)[0]))
for outlier in np.where(z > outlierThreshold):
  print("2:", outlier)
  data["cum_gain"][outlier] = data["cum_gain"][outlier] / 3
data["tracker_mean_denivelation"] = data["fitbitFloors"]
data = insert_data_to_tracker_mean_steps(period1, data, "fitbitFloors", "tracker_mean_denivelation")
data = insert_data_to_tracker_mean_steps(period2, data, "fitbitFloors", "tracker_mean_denivelation")
data = insert_data_to_tracker_mean_steps(period3, data, "fitbitFloors", "tracker_mean_denivelation")
data = insert_data_to_tracker_mean_steps(period4, data, "fitbitFloors", "tracker_mean_denivelation")
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period5, data, "cum_gain", "fitbitFloors", "tracker_mean_denivelation")
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period6, data, "elevation_gain", "fitbitFloors", "tracker_mean_denivelation")
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period7, data, "elevation_gain", "fitbitFloors", "tracker_mean_denivelation")

# Filling the "generalmood" column for time before Participant1 started recording it
data.loc[data.index < "2016-11-07", "generalmood"] = np.mean(data.loc[data.index >= "2016-11-07"]["generalmood"].tolist())

# Transforming pain scale
data["kneePain"]             = transformPain(data["kneePain"])
data["handsAndFingerPain"]   = transformPain(data["handsAndFingerPain"])
data["foreheadAndEyesPain"]  = transformPain(data["foreheadAndEyesPain"])
data["forearmElbowPain"]     = transformPain(data["forearmElbowPain"])
data["aroundEyesPain"]       = transformPain(data["aroundEyesPain"])
data["shoulderNeckPain"]     = transformPain(data["shoulderNeckPain"])
data["sick_tired"]           = transformPain(data["sick_tired"])
data["painInOtherRegion"]    = transformPain(data["painInOtherRegion"])
data["maxPainOtherThanKnee"] = data[["handsAndFingerPain", "foreheadAndEyesPain", "forearmElbowPain", "aroundEyesPain", "shoulderNeckPain", "sick_tired", "painInOtherRegion"]].max(axis=1)

# Selecting the time interval to look at the data
data = subset_period(data, "2016-01-05", "2019-10-20")

# Plotting results
fig, axes = plt.subplots(nrows=6, ncols=1)
# Steps
scaler = MinMaxScaler()
column_list = ["fitbitDistance", "movesSteps", "googlefitSteps", "basisPeakSteps", "tracker_mean_distance"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[0])
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Cumulated elevation gain
scaler = MinMaxScaler()
column_list = ["cum_gain", "elevation_gain", "fitbitFloors", "tracker_mean_denivelation"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[1])
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# All fitbit variables
# scaler = MinMaxScaler()
# column_list = ["fitbitCaloriesBurned", "fitbitSteps", "fitbitDistance", "fitbitFloors", "fitbitMinutesSedentary", "fitbitMinutesLightlyActive", "fitbitMinutesFairlyActive", "fitbitMinutesVeryActive", "fitbitActivityCalories"]
# data[column_list] = scaler.fit_transform(data[column_list])
# data[column_list].plot(ax=axes[2])
# axes[2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Time spent driving
data["timeDrivingCar"].plot(ax=axes[2])
axes[2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Mental state
data["generalmood"].plot(ax=axes[3])
axes[3].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Maximum pain in other regions
data["maxPainOtherThanKnee"].plot(ax=axes[4])
axes[4].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Knee pain
data["kneePain"].plot(ax=axes[5])
axes[5].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()

