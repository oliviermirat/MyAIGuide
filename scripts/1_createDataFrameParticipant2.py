"""
Created on Mon Aug 10 2020

@author: evadatinez
"""

# %% import libraries
import pickle
import numpy as np
import pandas as pd
from MyAIGuide.data.google_fit import get_google_fit_steps
from MyAIGuide.data.movesDataGatheredFromWebExport import movesDataGatheredFromWebExport
from MyAIGuide.data.storePainIntensitiesForParticipants2to9 import storePainIntensitiesForParticipants2to9
from MyAIGuide.data.calculateCumulatedElevationGainMoves import retrieve_stored_CEG_moves
from MyAIGuide.data.OruxTrace import OruxTrace


# %% Create master dataframe
dates = pd.date_range("2018-01-31", periods=852, freq="1D")

columnnames = [
        "googlefitSteps",
        "movesSteps",
        "happiness",
        "kneepain",
        "cum_gain_cycling",
        "cum_gain_walking",
        "oruxCumulatedElevationGain"
           ]

data = pd.DataFrame(np.nan, columns=columnnames, index=dates)

# %% Fill dataframe with data

# Directory to participant2 data
datadir = "../data/raw/ParticipantData/Participant2Anonymized/"

# Store Google fit steps
data = get_google_fit_steps(datadir, data)

# Storing moves data in dataframe
fname = "../data/raw/ParticipantData/Participant2Anonymized/MovesAppData/daily/summary/"
data = movesDataGatheredFromWebExport(fname, data)

# Retrieving stored cumulated elevation gain from moves app
fname = "../data/raw/ParticipantData/Participant2Anonymized/cum_gains_moves_participant2.csv"
data = retrieve_stored_CEG_moves(fname, data)

# Retrieving OruxTrace elevation gain data
fname = "../data/external/Participant2/OruxTrace/"
data = OruxTrace(data, fname)

# Store pain intensities
new_data = storePainIntensitiesForParticipants2to9(datadir, data)

# all columns to lowercase
new_data.columns = [col.lower() for col in new_data.columns]

# Saving the dataframe in a text
output = open("../data/preprocessed/preprocessedDataParticipant2.txt", "wb")
pickle.dump(new_data, output)
output.close()
