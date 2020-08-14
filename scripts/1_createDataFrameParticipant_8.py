#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 13:45:11 2020

@author: anniewong
"""

import pandas as pd
import pickle

from MyAIGuide.data.fitbitDataGatheredFromAPI import fitbitDataGatheredFromAPI
from MyAIGuide.data.store_diary_participant8 import store_retrieve_diary
from MyAIGuide.data.complaintsData import complaintsData


foldername = "../data/raw/ParticipantData/Participant8Anonymized/"
diary= "../data/external/myaiguideconfidentialdata/Participant8/Participant8diaries.json"

# timerange
dates = pd.date_range("2018-10-28", periods=552, freq="1D") #2020-05-01
data = pd.DataFrame(index = dates)

# participant8Fitbit.json
data = fitbitDataGatheredFromAPI(foldername, data)
data["steps"] = pd.to_numeric(data["steps"])

# Participant8Observations.csv
data = complaintsData(foldername, data)

# Participant8Pain.csv
data = storePainIntensitiesForParticipants2to9(foldername, data)

# Participant8 diaries
data = store_retrieve_diary(data, diary)

#   # Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant8" + ".txt", "wb")
pickle.dump(data, output)
output.close()
