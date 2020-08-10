#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 12:21:57 2020

@author: anniewong
"""

# This scripts assumes that the dataframe has been created and saved in data.txt

#%% Libraries
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

from MyAIGuide.utilities.dataFrameUtilities import insert_rolling_mean_columns

# Read file 
input = open("../data/preprocessed/preprocessedDataParticipant3.txt", "rb")
data = pickle.load(input)
input.close()
                        
#%% Preprocess data for plotting  

# Add rolling mean columns
columns=data.columns.tolist()
data=insert_rolling_mean_columns(data, columns, 21)

#%% Plot data

# happiness and patellartendonthrobbing contain too little data for plotting
# Kneepain data also contains many missing values
cols = ["googlefitsteps", "kneepain"]
colors = ["r","g",]
rm=["googlefitsteps_RollingMean","kneepain_RollingMean"]
colors2=["grey", "purple", "yellow"]

fig,axes = plt.subplots(2, sharex=True, sharey=True)

# ---- loop over axes ----
for i,ax in enumerate(axes):
  axes[i].plot(data[cols[i]], label=cols[i], color=colors[i])
  axes[i].plot(data[rm[i]], label=rm[i], color=colors2[i])
  axes[i].legend(loc="upper right")
plt.show()


