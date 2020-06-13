import pickle
import numpy as np
import pandas as pd
import sys
sys.path.insert(1, '../src/MyAIGuide/data')

from fitbitDataGatheredFromWebExport import fitbitDataGatheredFromWebExport
from movesDataGatheredFromWebExport import movesDataGatheredFromWebExport
from googleFitGatheredFromWebExport import googleFitGatheredFromWebExport
from storePainIntensitiesForParticipant1 import storePainIntensitiesForParticipant1
from retrieve_mentalstate_participant1 import retrieve_mentalstate_participant1
from storeSportDataParticipant1 import storeSportDataParticipant1
from storeManicTimeBlankScreen import storeManicTimeBlankScreen
from storeManicTime import storeManicTime

# Creation of the dataframe where everything will be stored
i = pd.date_range("2015-11-19", periods=1700, freq="1D")
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
    "generalmood": empty,
    "walk": empty,
    "roadBike": empty,
    "mountainBike": empty,
    "swimming": empty,
    "surfing": empty,
    "climbing": empty,
    "viaFerrata": empty,
    "alpiSki": empty,
    "downSki": empty,
    "climbingDenivelation": empty,
    "climbingMaxEffortIntensity": empty,
    "climbingMeanEffortIntensity": empty,
    "swimmingKm": empty,
    "manicTimeC1": empty,
    "manicTimeC2": empty,
    "manicTimeC3": empty,
    "manicTimeT": empty,
    "manicTimeBlankScreenC1": empty,
    "manicTimeBlankScreenC2": empty,
    "manicTimeBlankScreenC3": empty,
    "manicTimeBlankScreenT": empty,
    "manicTimeDelta": empty,
}
data = pd.DataFrame(data=d, index=i)

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

# Storing mental state in dataframe
filename = "../data/external/moodAndOtherVariables.csv"
data = retrieve_mentalstate_participant1(filename, data)

# Storing sport data in dataframe
filename = "../data/raw/ParticipantData/Participant1PublicOM/sport.csv"
data = storeSportDataParticipant1(filename, data)

# Storing Manic Time data in dataFrame
fname = "../data/raw/ParticipantData/Participant1PublicOM/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeManicTime(fname, numberlist, data)

# Storing Manic Time Blank Screen data in dataframe
fname = "../data/raw/ParticipantData/Participant1PublicOM/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeManicTimeBlankScreen(fname, numberlist, data)

# Create Manic Time Delta Column in dataframe
data['manicTimeDelta'] = data['manicTimeT'] - data['manicTimeBlankScreenT'].astype(int)

# Prints the dataframe
pd.set_option('display.max_rows', None)
print(data)

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant1.txt", "wb")
pickle.dump(data, output)
output.close()
