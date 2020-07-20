#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 12:18:43 2020

@author: anniewong
"""

#%% import libraries
import pickle
import numpy as np
import pandas as pd
from MyAIGuide.data.google_fit import get_google_fit_steps
from MyAIGuide.data.storePainIntensitiesForParticipants2to9 import storePainIntensitiesForParticipants2to9


#%% Create master dataframe
dates = pd.date_range("2018-10-22", periods=289, freq="1D") 

columnnames = [
        "googlefitSteps",
        "happiness",
        "kneepain", 
        'patellartendonthrobbing'
           ]

data = pd.DataFrame(np.nan, columns = columnnames, index = dates)

#%% Fill dataframe with data

# Directory to participant4 data
datadir = "../data/raw/ParticipantData/Participant3Anonymized/"

# Store Google fit steps
new_data=get_google_fit_steps(datadir, data)

# Store pain intensities 
new_data= storePainIntensitiesForParticipants2to9(datadir, new_data)

# all columns to lowercase
new_data.columns = [col.lower() for col in new_data.columns]

# Saving the dataframe in a text
output = open("../data/preprocessed/preprocessedDataParticipant3.txt", "wb")
pickle.dump(new_data, output)
output.close()
