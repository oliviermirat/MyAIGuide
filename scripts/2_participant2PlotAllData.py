"""
Created on Mon Aug 24 2020

@author: evadatinez
"""

# This scripts assumes that the dataframe has been created and saved in data.txt

#%% Libraries
import pickle

from MyAIGuide.utilities.dataFrameUtilities import insert_rolling_mean_columns

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

# Set global plot parameters 
plt.rcParams['figure.figsize'] = [12, 6]
plt.rcParams['figure.dpi'] = 80

# Read file 
input = open("../data/preprocessed/preprocessedDataParticipant2.txt", "rb")
data = pickle.load(input)
input.close()
                        
#%% Preprocess data for plotting  

# Add rolling mean columns
columns=data.columns.tolist()
data=insert_rolling_mean_columns(data, columns, 21)

#%% Plot data

# cum_gain_cycling and happiness contain too little data for plotting
# Kneepain data also contains many missing values
cols = ['cum_gain_walking', 'googlefitsteps', 'kneepain', 'movessteps']
rm=['cum_gain_walking_RollingMean', 'googlefitsteps_RollingMean', 'kneepain_RollingMean', 'movessteps_RollingMean']

fig,axes = plt.subplots(4, sharex=True, sharey=True)

# ---- loop over axes ----
for i,ax in enumerate(axes):
  axes[i].plot(data[cols[i]], label=cols[i])
  axes[i].plot(data[rm[i]], label=rm[i])
  axes[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()