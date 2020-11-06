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
input = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Plotting results for knee pain and related variables
fig, axes = plt.subplots(nrows=2, ncols=1)
scaler = MinMaxScaler()
column_list = ["tracker_mean_distance", "tracker_mean_denivelation", "timeDrivingCar", "swimmingKm", "cycling"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[0])
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
data["kneePain"].plot(ax=axes[1])
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

# Plotting results for hands, finger and forearm elbow pain and related variables
fig, axes = plt.subplots(nrows=2, ncols=1)
scaler = MinMaxScaler()
column_list = ["whatPulseT_corrected", "climbingDenivelation", "climbingMaxEffortIntensity", "climbingMeanEffortIntensity", "swimmingKm", "surfing", "viaFerrata"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[0])
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# data["handsAndFingerPain"].plot(ax=axes[1])
# data["forearmElbowPain"].plot(ax=axes[1])
data["fingerHandArmPain"].plot(ax=axes[1])
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

# Plotting results for around eyes pain and related variables
fig, axes = plt.subplots(nrows=2, ncols=1)
scaler = MinMaxScaler()
column_list = ["manicTimeDelta_corrected", "timeDrivingCar"]
data[column_list] = scaler.fit_transform(data[column_list])
data[column_list].plot(ax=axes[0])
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
data["foreheadEyesPain"].plot(ax=axes[1])
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

