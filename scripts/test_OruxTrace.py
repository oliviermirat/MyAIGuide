import pickle
import numpy as np
import pandas as pd
import sys
sys.path.insert(1, '../src/MyAIGuide/data')

from OruxTrace import OruxTrace
from OruxTrace import get_gain


# Creation of the dataframe where everything will be stored
dates = pd.date_range("2015-11-19", periods=1700, freq="1D")

columnname = ['oruxCumulatedElevationGain']

data = pd.DataFrame(np.nan, columns=columnname, index=dates)

# Directory to participant2 data 
fname = "../data/raw/ParticipantData/Participant2Anonymized/OruxTrace/" # path in local repo --> needs to be adjusted for general testing

# Storing OruxTrace data in dataframe
data = OruxTrace(data, fname)
print(data)

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant2.txt", "wb")
pickle.dump(data, output)
output.close()