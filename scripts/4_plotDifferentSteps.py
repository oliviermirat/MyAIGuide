# This scripts assumes that the dataframe has been created and saved in data.txt

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dataFrameUtilities import (
    addDataToTrackerMeanSteps,
    addInsultIntensityColumns,
    adjustVarAndPlaceInData,
    getInsultAboveThreshold,
    getPainAboveThreshold,
    selectColumns,
    selectTime,
)
from sklearn.preprocessing import MinMaxScaler

# Getting data
input = open("../data/preprocessed/preprocessedDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

# Removing "steps" caused by scooter riding
data["steps"] = data["steps"] - 37 * data["scooterRiding"]
data["steps"][data["steps"] < 0] = 0

# Selecting the different periods where different trackers where used
period1 = selectTime(data, "2015-12-26", "2016-06-21")  # basis and googlefit
period2 = selectTime(data, "2016-06-22", "2016-09-01")  # basis
period3 = selectTime(data, "2016-09-02", "2017-01-01")  # basis and fitbit
period4 = selectTime(data, "2017-01-02", "2017-10-16")  # fitbit
period5 = selectTime(data, "2017-10-17", "2018-07-02")  # fitbit and moves
period6 = selectTime(data, "2018-07-03", "2018-07-30")  # fitbit and moves and googlefit
period7 = selectTime(data, "2018-07-31", "2020-02-01")  # fitbit and googlefit

# Creating the trackerMeanSteps variable in the dataframe and puts harmonized steps value inside
data["trackerMeanSteps"] = data["steps"]
data = adjustVarAndPlaceInData(period1, data, "googlefitSteps", "basisPeakSteps", "2015-12-26", "2016-06-21")
data = addDataToTrackerMeanSteps(period2, data, "basisPeakSteps", "2016-06-22", "2016-09-01")
data = adjustVarAndPlaceInData(period3, data, "basisPeakSteps", "steps", "2016-09-02", "2017-01-01")
data = addDataToTrackerMeanSteps(period4, data, "steps", "2017-01-02", "2017-10-16")
data = adjustVarAndPlaceInData(period5, data, "movesSteps", "steps", "2017-10-17", "2018-07-02")
data = adjustVarAndPlaceInData(period6, data, "movesSteps", "steps", "2018-07-03", "2018-07-30")
data = adjustVarAndPlaceInData(period7, data, "googlefitSteps", "steps", "2018-07-31", "2020-02-01")

# Plotting results

steps = selectColumns(data, ["steps", "movesSteps", "googlefitSteps", "basisPeakSteps", "trackerMeanSteps"])
fig, axes = plt.subplots(nrows=2, ncols=1)
steps.plot(ax=axes[0])
selectColumns(data, ["trackerMeanSteps"]).plot(ax=axes[1])
leg = plt.legend(loc="best")
leg.set_draggable(True)
plt.show()
