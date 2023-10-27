import csv
import datetime
import os
import os.path
import pickle
import re
import numpy as np
import pandas as pd

import sys
sys.path.insert(1, '../src/MyAIGuide/data')

from google_fit import get_google_fit_steps
from fitbitDataGatheredFromAPI import fitbitDataGatheredFromAPI
from storePainIntensitiesForParticipants2to9 import storePainIntensitiesForParticipants2to9

participant_ids = [3, 4, 5, 6, 7, 9]

# Time range during which each Participant recorded data
time_ranges = {3 : {"startdate": "2018-10-01", "periods" : 400},
               4 : {"startdate": "2019-04-12", "periods" : 60},
               5 : {"startdate": "2019-04-23", "periods" : 60},
               6 : {"startdate": "2019-06-01", "periods" : 100},
               7 : {"startdate": "2016-02-01", "periods" : 1370},
               9 : {"startdate": "2019-10-14", "periods" : 75}}

# Parameters available for each Participants
columnnamesId = {3 : ["googlefitSteps", "kneepain", "happiness"],
                 4 : ["steps", "kneepain", "elbowpain", "happiness"],
                 5 : ["steps", "anklepain"],
                 6 : ["googlefitSteps", "kneepain"],
                 7 : ["steps", "hippain", "shoulderpain", "happiness"],
                 9 : ["steps", "kneepain", "happiness"]}

for participant_id in participant_ids:
  
  print("\nCreating dataframe for participant " + str(participant_id))

  # Creation of empty dataframe
  dates = pd.date_range(time_ranges[participant_id]["startdate"], periods=time_ranges[participant_id]["periods"], freq="1D")
  columnnames = columnnamesId[participant_id]
  data = pd.DataFrame(np.nan, columns = columnnames, index = dates)

  # Folder where the data is stored
  foldername = "../data/raw/ParticipantData/Participant" + str(participant_id) + "Anonymized/"

  # Storing fitbit data in dataframe
  if "steps" in columnnames:
    data = fitbitDataGatheredFromAPI(foldername, data)
    data["steps"] = pd.to_numeric(data["steps"])
  
  # Storing GoogleFit data in dataframe
  if "googlefitSteps" in columnnames:
    data = get_google_fit_steps(foldername, data)

  # Storing pain intensities in dataframe
  data = storePainIntensitiesForParticipants2to9(foldername, data)

  # Saving the dataframe in a txt
  output = open("../data/preprocessed/preprocessedDataParticipant" + str(participant_id) + ".txt", "wb")
  pickle.dump(data, output)
  output.close()
  