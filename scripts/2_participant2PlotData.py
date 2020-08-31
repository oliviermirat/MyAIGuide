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
input = open("../data/preprocessed/preprocessedDataParticipant2.txt", "rb")
data = pickle.load(input)
input.close()

data["kneepain"] = transformPain(data["kneepain"])

# Plotting results
fig, axes = plt.subplots(nrows=6, ncols=1)
# Steps
cols = ['movessteps', 'cum_gain_walking', 'googlefitsteps', 'elevation_gain', 'oruxcumulatedelevationgain', 'kneepain']
for idx, val in enumerate(cols):
  if val == 'oruxcumulatedelevationgain':
    data[val].plot(ax=axes[idx], color='green', marker='o', linestyle='dashed', markersize=2)
  else:
    data[val].plot(ax=axes[idx])
  axes[idx].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()
