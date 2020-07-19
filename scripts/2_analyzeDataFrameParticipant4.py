# This scripts assumes that the dataframe has been created and saved in data.txt

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MyAIGuide.utilities.dataFrameUtilities import (
    subset_period,
    insert_data_to_tracker_mean_steps,
    adjust_var_and_place_in_data,
    insert_rolling_mean_columns
)
from sklearn.preprocessing import MinMaxScaler

input = open("../data/preprocessed/preprocessedDataParticipant4.txt", "rb")
data = pickle.load(input)
input.close()

# Define period
period = subset_period(data, "2019-04-01", "2019-07-01")

# Scaling and selecting columns for plotting (variable happiness with too few datapoints)

scaler = MinMaxScaler()
period[["elbowpain", "kneepain", "steps"]] = scaler.fit_transform(period[["elbowpain", "kneepain", "steps"]])
pd.set_option('display.max_rows', None)
print(period)

elbowpain = pd.to_numeric(period["elbowpain"])
kneepain = pd.to_numeric(period["kneepain"])
steps = pd.to_numeric(period["steps"])


# Get rolling means
#elbowpain_mean = insert_rolling_mean_columns(period, ["elbowpain"], 21)
#kneepain = insert_rolling_mean_columns(period, ["kneewpain"], 21)
#happiness = insert_rolling_mean_columns(period, ["happiness"], 21)
#steps_rolling_mean = insert_rolling_mean_columns(period, ["steps"], 21)


# Plotting
fig, axes = plt.subplots(nrows=4, ncols=1)

axes[0].plot(elbowpain, label= 'elbowpain', color='red')
axes[1].plot(kneepain, label='kneepain', color='blue')
#axes[2].plot(happiness, label='happiness', color='green') --> too few datapoints 
axes[2].plot(steps, label='steps', color='purple')
#axes[2].plot(steps_rolling_mean, color='grey')
axes[3].plot(elbowpain, label= 'elbowpain', color='red')
axes[3].plot(kneepain, label='kneepain', color='blue')
axes[3].plot(steps, label='steps', color='purple')

axes[0].legend(loc='upper right')
axes[1].legend(loc='upper right')
axes[2].legend(loc='upper right')
axes[3].legend(loc='upper right')

plt.show()
