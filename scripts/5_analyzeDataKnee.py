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

input = open("data.txt", "rb")
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
data = adjustVarAndPlaceInData(
    period1, data, "googlefitSteps", "basisPeakSteps", "2015-12-26", "2016-06-21"
)
data = addDataToTrackerMeanSteps(
    period2, data, "basisPeakSteps", "2016-06-22", "2016-09-01"
)
data = adjustVarAndPlaceInData(
    period3, data, "basisPeakSteps", "steps", "2016-09-02", "2017-01-01"
)
data = addDataToTrackerMeanSteps(period4, data, "steps", "2017-01-02", "2017-10-16")
data = adjustVarAndPlaceInData(
    period5, data, "movesSteps", "steps", "2017-10-17", "2018-07-02"
)
data = adjustVarAndPlaceInData(
    period6, data, "movesSteps", "steps", "2018-07-03", "2018-07-30"
)
data = adjustVarAndPlaceInData(
    period7, data, "googlefitSteps", "steps", "2018-07-31", "2020-02-01"
)

data["steps"] = data["trackerMeanSteps"]

# selecting the time interval
timeSelected = selectTime(data, "2015-12-26", "2019-10-20")


# Getting knee pain information

kneePain = selectColumns(timeSelected, ["kneePain"])

thres = kneePain.copy()
thres[:] = 3.3


# Calculating knee stress over time

env = addInsultIntensityColumns(timeSelected, ["steps", "kneePain"], 21, 30)
envRollingMean = selectColumns(env, ["stepsInsultIntensity"])
envMaxInsultDiff = selectColumns(env, ["stepsMaxInsultDiff"])

kneePainRollingMean = selectColumns(env, ["kneePainInsultIntensity"])
kneePainRollingMean = kneePainRollingMean.replace(0, 0.4)
scaler = MinMaxScaler()
kneePainRollingMeanArray = scaler.fit_transform(kneePainRollingMean)
for i in range(0, len(kneePainRollingMean)):
    kneePainRollingMean["kneePainInsultIntensity"][i] = kneePainRollingMeanArray[i]
kneePainRollingMean = kneePainRollingMean.replace(0.0, 0.4)

thres2 = kneePain.copy()
thres2[:] = 1.2
for i in range(0, 275):
    thres2["kneePain"][i] = 0.8
for i in range(1100, len(thres2)):
    thres2["kneePain"][i] = 1.4

envBrut = selectColumns(env, ["steps"])

betterMaxInsult = envMaxInsultDiff.copy()
scaler = MinMaxScaler()
betterMaxInsultArray = scaler.fit_transform(betterMaxInsult)
for i in range(0, len(betterMaxInsult)):
    betterMaxInsult["stepsMaxInsultDiff"][i] = (
        betterMaxInsultArray[i]
        + envBrut["steps"][i]
        + kneePainRollingMean["kneePainInsultIntensity"][i]
    )


# Finding time points where knee pain and knee stress are above a certain threshold

painAboveThresh = getPainAboveThreshold(kneePain, "kneePain", 3.3)
painAboveThresh = selectColumns(painAboveThresh, ["kneePainThreshed"])

stepsMaxInsultDiffThresh = getInsultAboveThreshold(
    betterMaxInsult, "stepsMaxInsultDiff", thres2
)
stepsMaxInsultDiffThresh = selectColumns(
    stepsMaxInsultDiffThresh, ["stepsMaxInsultDiffThreshed"]
)


# Plotting results

fig, axes = plt.subplots(nrows=3, ncols=1)

selectColumns(kneePain, ["kneePain"]).rename(columns={"kneePain": "knee pain"}).plot(
    ax=axes[0]
)
thres.rename(columns={"kneePain": "pain threshold"}).plot(ax=axes[0])

selectColumns(betterMaxInsult, ["stepsMaxInsultDiff"]).rename(
    columns={"stepsMaxInsultDiff": "knee stress"}
).plot(ax=axes[1])
thres2.rename(columns={"kneePain": "knee stress threshold"}).plot(ax=axes[1])

painAboveThresh.rename(
    columns={"kneePainThreshed": "knee pain is above threshold"}
).plot(ax=axes[2])
stepsMaxInsultDiffThresh = 0.95 * stepsMaxInsultDiffThresh
stepsMaxInsultDiffThresh.rename(
    columns={"stepsMaxInsultDiffThreshed": "knee stress is above threshold"}
).plot(ax=axes[2])

leg = plt.legend(loc="best")
# leg.draggable()
plt.show()
