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

from storeBasisPeakInDataFrame import storeBasisPeakInDataFrame
from fitbitDataGatheredFromWebExport import fitbitDataGatheredFromWebExport
from movesDataGatheredFromWebExport import movesDataGatheredFromWebExport
from googleFitGatheredFromWebExport import googleFitGatheredFromWebExport
from storePainIntensitiesForParticipant1 import storePainIntensitiesForParticipant1
from storeWhatPulse import storeWhatPulse
from storeManicTime import storeManicTime
from storeEyeRelatedActivitiesParticipant1 import storeEyeRelatedActivitiesParticipant1
from storeSportDataParticipant1 import storeSportDataParticipant1

# Creation of the dataframe where everything will be stored
i = pd.date_range("2015-11-19", periods=1700, freq="1D")
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {
    "basisPeakSteps": empty,
    "steps": empty,
    "denivelation": empty,
    "kneePain": empty,
    "handsAndFingerPain": empty,
    "foreheadAndEyesPain": empty,
    "forearmElbowPain": empty,
    "aroundEyesPain": empty,
    "shoulderNeckPain": empty,
    "painthreshold": np.full((sLength), 3.4),
    "whatPulseKeysC1": empty,
    "whatPulseClicksC1": empty,
    "manicTimeC1": empty,
    "whatPulseKeysC2": empty,
    "whatPulseClicksC2": empty,
    "manicTimeC2": empty,
    "whatPulseKeysC3": empty,
    "whatPulseClicksC3": empty,
    "manicTimeC3": empty,
    "whatPulseKeysT": empty,
    "whatPulseClicksT": empty,
    "whatPulseT": empty,
    "manicTimeT": empty,
    "walk": empty,
    "roadBike": empty,
    "mountainBike": empty,
    "swimming": empty,
    "surfing": empty,
    "climbing": empty,
    "viaFerrata": empty,
    "alpiSki": empty,
    "downSki": empty,
    "eyeRelatedActivities": empty,
    "scooterRiding": empty,
    "movesSteps": empty,
    "googlefitSteps": empty,
}
data = pd.DataFrame(data=d, index=i)

# Storing BasisPeak data in dataframe
if (False):  # This step takes a long time, put to False if you want to skip it, and to True otherwise
    filename = "../data/raw/ParticipantData/Participant1PublicOM/bodymetrics.csv"
    data = storeBasisPeakInDataFrame(filename, data)

# Storing fitbit data in dataframe
fname = "../data/raw/ParticipantData/Participant1PublicOM/dailyFitBitPerMonth/"
data = fitbitDataGatheredFromWebExport(fname, data)

# Storing moves data in dataframe
fname = "../data/raw/ParticipantData/Participant1PublicOM/MovesAppData/yearly/summary/"
data = movesDataGatheredFromWebExport(fname, data)

# Storing google fit data in dataframe
filename1 = "../data/raw/ParticipantData/Participant1PublicOM/GoogleFitData/smartphone1/dailyAggregations/dailySummaries.csv"
filename2 = "../data/raw/ParticipantData/Participant1PublicOM/GoogleFitData/smartphone2/dailyAggregations/dailySummaries.csv"
data = googleFitGatheredFromWebExport(filename1, filename2, data)

# Storing pain intensities in dataframe
filename = "../data/raw/ParticipantData/Participant1PublicOM/pain.csv"
data = storePainIntensitiesForParticipant1(filename, data)

# Storing whatPulse data in dataFrame
fname = "../data/raw/ParticipantData/Participant1PublicOM/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeWhatPulse(fname, numberlist, data)

# Storing Manic Time data in dataFrame
fname = "../data/raw/ParticipantData/Participant1PublicOM/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeManicTime(fname, numberlist, data)

# Storing Sport data in dataframe
filename = "../data/raw/ParticipantData/Participant1PublicOM/sport.csv"
data = storeSportDataParticipant1(filename, data)

# Storing Eye related activity hours in dataframe
filename = "../data/raw/ParticipantData/Participant1PublicOM/eyeRelatedActivities.csv"
data = storeEyeRelatedActivitiesParticipant1(filename, data)

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant1.txt", "wb")
pickle.dump(data, output)
output.close()
