# This scripts assumes that the dataframe has been created and saved in data.txt

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dataFrameUtilities import addRollingMeanColumns, selectColumns, selectTime
from sklearn.preprocessing import MinMaxScaler

input = open("../data/preprocessed/preprocessedDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

timeSelected = selectTime(data, "2016-03-01", "2019-03-06")

timeSelected["foreheadAndEyesPain"] = timeSelected["foreheadAndEyesPain"] + timeSelected["aroundEyesPain"]
pain = selectColumns(timeSelected, ["foreheadAndEyesPain"])
pain = addRollingMeanColumns(pain, ["foreheadAndEyesPain"], 21)

env = addRollingMeanColumns(timeSelected, ["manicTimeT", "eyeRelatedActivities"], 21)
envRollingMean = selectColumns(env, ["manicTimeTRollingMean", "eyeRelatedActivitiesRollingMean"])
envBrut = selectColumns(env, ["manicTimeT", "eyeRelatedActivities"])

fig, axes = plt.subplots(nrows=3, ncols=1)

pain.plot(ax=axes[0])
envBrut.plot(ax=axes[1])
envRollingMean.plot(ax=axes[2])

leg = plt.legend(loc="best")
leg.set_draggable(True)
plt.show()
