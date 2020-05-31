#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:16:41 2020

@author: anniewong
"""

#%% import libraries
import pickle
import numpy as np
import pandas as pd
import sys
sys.path.insert(1, '../src/MyAIGuide/data')

from fitbitDataGatheredFromAPI import fitbitDataGatheredFromAPI
from storePainIntensitiesForParticipants2to9 import storePainIntensitiesForParticipants2to9

 
#%% Creation of the dataframe where everything will be stored
dates = pd.date_range("2019-04-09", periods=80, freq="1D")

columnnames = [
        "abdominalPain",
        "anklePain",
        "aroundEyesPain",     
        "denivelation",
        "foreheadAndEyesPain",
        "footPain",
        "forearmElbowPain",
        "googlefitSteps",
        "handsAndFingerPain",
        "happiness",
        "headache", 
        "hipPain", 
        "kneePain", 
        "legPain",
        "lowBackPain",
        "movesSteps",
        "patellarTendonThrobbing",
        "shoulderNeckPain",
        "steps"
           ]

data = pd.DataFrame(np.nan, columns = columnnames, index = dates)

# datadir = "../data/raw/ParticipantData/Participant9Anonymized/"

#%% Fill dataframe with data

# Directory to participant4 data
datadir = "../data/raw/ParticipantData/Participant4Anonymized/"

# Storing fitbit data in dataframe
data = fitbitDataGatheredFromAPI(datadir, data)

# Storing pain intensities in dataframe
data= storePainIntensitiesForParticipants2to9(datadir, data)

#%%
# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant4.txt", "wb")
pickle.dump(data, output)
output.close()