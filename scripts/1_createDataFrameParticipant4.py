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

from storePainIntensitiesForParticipants2to9 import storePainIntensitiesForParticipants2to9
from fitbitDataGatheredFromAPI import fitbitDataGatheredFromAPI


# Creation of the dataframe where everything will be stored
dates = pd.date_range("2015-11-19", periods=1700, freq="1D")

columnnames = [
    "steps",
    "kneepain", 
    "elbowpain",
    "happiness", 
        ]

data = pd.DataFrame(np.nan, columns = columnnames, index = dates)

filename = "../data/raw/ParticipantData/Participant4Anonymized/"

# Storing fitbit data in dataframe
data = fitbitDataGatheredFromAPI(filename, data)

# Storing pain intensities in dataframe
data = storePainIntensitiesForParticipants2to9(filename, data)

pd.set_option('display.max_rows', None)
print(data)

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant4.txt", "wb")
pickle.dump(data, output)
output.close()