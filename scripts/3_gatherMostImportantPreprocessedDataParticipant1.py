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

# Filling the "tracker_mean_denivelation" column for time before Participant1 started recording it
data.loc[data.index < "2016-09-01", "tracker_mean_denivelation"] = np.mean(data.loc[data.index >= "2016-09-01"]["tracker_mean_denivelation"].tolist())

# Filling the "generalmood" column for time before Participant1 started recording it
data.loc[data.index < "2016-11-07", "generalmood"] = np.mean(data.loc[data.index >= "2016-11-07"]["generalmood"].tolist())

# Adjusting WhatPulse for missing data (0 values)
period1 = ("2015-12-26", "2020-02-01") #("2015-12-26", "2020-02-01")
data["whatPulseT_corrected"] = data["whatPulseT"]
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period1, data, "manicTimeDelta", "whatPulseT", "whatPulseT_corrected")

# Adjusting ManicTime for missing data (0 values)
period1 = ("2015-12-26", "2020-02-01") #("2015-12-26", "2020-02-01")
data["manicTimeDelta_corrected"] = data["manicTimeDelta"]
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period1, data, "whatPulseT", "manicTimeDelta", "manicTimeDelta_corrected")

# Pain in Various locations
data["kneePain"]             = transformPain(data["kneePain"])
a = data["handsAndFingerPain"].tolist()
b = data["forearmElbowPain"].tolist()
data["fingerHandArmPain"]    = transformPain(np.array([max(a[i], b[i]) for i, val in enumerate(a)]))
data["shoulderNeckPain"]     = transformPain(data["shoulderNeckPain"]) # add this to the previous???
a = data["foreheadAndEyesPain"].tolist()
b = data["aroundEyesPain"].tolist()
data["foreheadEyesPain"]     = transformPain(np.array([max(a[i], b[i]) for i, val in enumerate(a)]))
data["sick_tired"]           = transformPain(data["sick_tired"])

# Cycling
data["cycling"] = data["roadBike"] + data["mountainBike"]

# Select time period
data = data.loc[data.index >= "2016-01-01"]
data = data.loc[data.index <= "2019-12-22"]

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "wb")
pickle.dump(data[["tracker_mean_distance", "tracker_mean_denivelation", "whatPulseT_corrected", "manicTimeDelta_corrected", "timeDrivingCar", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "climbing", "viaFerrata", "swimming", "cycling", "generalmood", "kneePain", "fingerHandArmPain", "shoulderNeckPain", "foreheadEyesPain", "sick_tired"]], output)
output.close()
