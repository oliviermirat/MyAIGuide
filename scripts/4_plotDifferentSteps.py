# This scripts assumes that the dataframe has been created and saved in .txt

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

from dataFrameUtilities import (
    insert_data_to_tracker_mean_steps,
    adjust_var_and_place_in_data
)
from sklearn.preprocessing import MinMaxScaler


# Set global plot parameters
plt.rcParams['figure.figsize'] = [12, 6]
plt.rcParams['figure.dpi'] = 80

# Getting data
data_path = "../data/preprocessed/preprocessedDataParticipant1.txt"
input = open(data_path, "rb")
data = pickle.load(input)
input.close()

# Removing "steps" caused by scooter riding
data["steps"] = data["steps"] - 37 * data["scooterRiding"]
data["steps"][data["steps"] < 0] = 0

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
data["tracker_mean_steps"] = data["steps"]
data = adjust_var_and_place_in_data(period1, data,
                                    "googlefitSteps", "basisPeakSteps")
data = insert_data_to_tracker_mean_steps(period2, data, "basisPeakSteps")
data = adjust_var_and_place_in_data(period3, data,
                                    "basisPeakSteps", "steps")
data = insert_data_to_tracker_mean_steps(period4, data, "steps")
data = adjust_var_and_place_in_data(period5, data,
                                    "movesSteps", "steps")
data = adjust_var_and_place_in_data(period6, data,
                                    "movesSteps", "steps")
data = adjust_var_and_place_in_data(period7, data,
                                    "googlefitSteps", "steps")

# Plotting results
columns_to_select = ["steps", "movesSteps", "googlefitSteps",
                     "basisPeakSteps", "tracker_mean_steps"]
steps = data[columns_to_select]
fig, axes = plt.subplots(nrows=2, ncols=1)
steps.plot(ax=axes[0])
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
data["tracker_mean_steps"].plot(ax=axes[1])
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()
