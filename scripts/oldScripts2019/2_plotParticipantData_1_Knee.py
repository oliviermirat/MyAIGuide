# This scripts assumes that the dataframe has been created and saved in data.txt

import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dataFrameUtilities import insert_rolling_mean_columns, subset_period

input = open("../data/preprocessed/preprocessedDataParticipant1.txt", "rb")
data = pickle.load(input)
input.close()

timeSelected = subset_period(data, "2016-09-01", "2019-10-20")

# pain = selectColumns(timeSelected, ["kneePain"])
pain = insert_rolling_mean_columns(timeSelected, ["kneePain"], 21)

env = insert_rolling_mean_columns(timeSelected, ["steps", "denivelation"], 21)
# envRollingMean = selectColumns(env, ["stepsRollingMean", "denivelationRollingMean"])
# envBrut = selectColumns(env, ["steps", "denivelation"])

fig, axes = plt.subplots(nrows=3, ncols=1)

pain["kneePain"].plot(ax=axes[0])
env[["steps", "denivelation"]].plot(ax=axes[1])
# envRollingMean.plot(ax=axes[2])

leg = plt.legend(loc="best")
leg.set_draggable(True)
plt.show()
