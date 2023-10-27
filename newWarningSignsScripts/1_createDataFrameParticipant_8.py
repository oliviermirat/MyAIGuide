#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 13:45:11 2020

@author: anniewong
"""

import pandas as pd
import pickle

import sys
sys.path.insert(1, '../src/MyAIGuide/data')

from fitbitDataGatheredFromAPI import fitbitDataGatheredFromAPI
from store_diary_participant8 import store_retrieve_diary
from complaintsData import complaintsData
from storePainIntensitiesForParticipants2to9 import storePainIntensitiesForParticipants2to9

foldername = "../data/raw/ParticipantData/Participant8Anonymized/"
diary= "../data/external/myaiguideconfidentialdata/Participant8/Participant8diaries.json"

# Create empty dataframe to fill
data = pd.DataFrame()

# Participant8 diaries
data = store_retrieve_diary(data, diary)

# participant8Fitbit.json
data = fitbitDataGatheredFromAPI(foldername, data)
data["steps"] = pd.to_numeric(data["steps"])

# Participant8Observations.csv
data = complaintsData(foldername, data)

# Participant8Pain.csv
data = storePainIntensitiesForParticipants2to9(foldername, data)

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant8" + ".txt", "wb")
pickle.dump(data, output)
output.close()
