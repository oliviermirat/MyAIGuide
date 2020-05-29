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
from MyAIGuide.data.fitbitDataGatheredFromAPI import fitbitDataGatheredFromAPI

sys.path.insert(1, '../src/MyAIGuide/data')


#%% Creation of the dataframe where everything will be stored

i = pd.date_range("2019-04-09", periods=80, freq="1D")
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {
    "steps": empty,
    "denivelation": empty,
    "kneePain": empty,
    "handsAndFingerPain": empty,
    "foreheadAndEyesPain": empty,
    "forearmElbowPain": empty,
    "aroundEyesPain": empty,
    "shoulderNeckPain": empty,
    "movesSteps": empty,
    "googlefitSteps": empty,
}
data = pd.DataFrame(data=d, index=i)

#%% Fill dataframe with data

# Storing fitbit data in dataframe
fname = "../data/raw/ParticipantData/Participant4Anonymized/"
data = fitbitDataGatheredFromAPI(fname, data)


#%%
# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant4.txt", "wb")
pickle.dump(data, output)
output.close()