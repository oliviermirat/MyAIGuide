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

import peaksAnalysis_launch


participant_ids = [3, 4, 5, 6, 7, 9]

columnnamesId = {3 : ["googlefitsteps", "kneepain"],     # not enough values for "happiness"
                 4 : ["steps", "kneepain", "elbowpain"], # not enough values for "happiness"
                 5 : ["steps", "anklepain"],
                 6 : ["googlefitsteps", "kneepain"],
                 7 : ["steps", "hippain", "shoulderpain", "happiness"],
                 9 : ["steps", "kneepain", "happiness"]}

for participant_id in participant_ids:
  
  print("\nPlotting dataframe for participant " + str(participant_id))
                 
  input = open("../data/preprocessed/preprocessedDataParticipant" + str(participant_id) + ".txt", "rb")
  data = pickle.load(input)
  input.close()
  
  data[columnnamesId[participant_id][1]] = data[columnnamesId[participant_id][1]].fillna(1)
  # data[columnnamesId[participant_id][1]] = data[columnnamesId[participant_id][1]].fillna(3) # Need to improve this
  
  # Analysis parameters
  parameters = {'rollingMeanWindow': 7, 'rollingMinMaxScalerWindow': 0, 'rollingMedianWindow': 7, 'minProminenceForPeakDetect': 0.01, 'windowForLocalPeakMinMaxFind': 5, 'plotGraph': True}
  
  plotGraphs = True
  
  peaksAnalysis_launch.calculateForAllRegionsParticipant3_4_5_6_7_9(data, parameters, plotGraphs, columnnamesId[participant_id][0], columnnamesId[participant_id][1])

