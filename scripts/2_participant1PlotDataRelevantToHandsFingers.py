# This scripts assumes that the dataframe has been created and saved in data.txt

import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from dataFrameUtilities import check_if_zero_then_adjust_var_and_place_in_data, insert_data_to_tracker_mean_steps, subset_period, transformPain, predict_values

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Transforming pain scale
data["kneePain"]             = transformPain(data["kneePain"])
data["handsAndFingerPain"]   = transformPain(data["handsAndFingerPain"])
data["foreheadAndEyesPain"]  = transformPain(data["foreheadAndEyesPain"])
data["forearmElbowPain"]     = transformPain(data["forearmElbowPain"])
data["aroundEyesPain"]       = transformPain(data["aroundEyesPain"])
data["shoulderNeckPain"]     = transformPain(data["shoulderNeckPain"])
data["sick_tired"]           = transformPain(data["sick_tired"])
data["painInOtherRegion"]    = transformPain(data["painInOtherRegion"])
data["maxPainOtherThanHandsAndFinger"] = data[["kneePain", "foreheadAndEyesPain", "forearmElbowPain", "aroundEyesPain", "shoulderNeckPain", "sick_tired", "painInOtherRegion"]].max(axis=1)

# Filling the "generalmood" column for time before Participant1 started recording it
data.loc[data.index < "2016-11-07", "generalmood"] = np.mean(data.loc[data.index >= "2016-11-07"]["generalmood"].tolist())

# Adjusting WhatPulse for missing data (0 values)
period1 = ("2015-12-26", "2020-02-01") #("2015-12-26", "2020-02-01")
data["whatPulseT_corrected"] = data["whatPulseT"]
[data, reg] = check_if_zero_then_adjust_var_and_place_in_data(period1, data, "manicTimeDelta", "whatPulseT", "whatPulseT_corrected")

# Selecting the time interval to look at the data
data = subset_period(data, "2016-01-05", "2019-10-20")

# Plotting results
fig, axes = plt.subplots(nrows=6, ncols=1)
# Number of clicks made on computer (both clicks and key presses)
scaler = MinMaxScaler()
column_list = ["whatPulseT", "whatPulseT_corrected"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[0])
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Physical activities related to hand and finger pain
scaler = MinMaxScaler()
column_list = ["surfing", "climbing", "viaFerrata", "swimming"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[1])
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# More details on climbing intensity and swimming distance
scaler = MinMaxScaler()
column_list = ["climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[2])
axes[2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Mental state
data["generalmood"].plot(ax=axes[3])
axes[3].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Maximum pain in other regions
data["maxPainOtherThanHandsAndFinger"].plot(ax=axes[4])
axes[4].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# Hands and finger pain
data["handsAndFingerPain"].plot(ax=axes[5])
axes[5].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()

