# In addition to all the data inside the folder ./data/raw/
# this scripts also requires the file moodAndOtherVariables.csv to be placed inside the folder ./data/external/myaiguideconfidentialdata/Participant1/

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
from google_fit import get_google_fit_activities
from storePainIntensitiesForParticipant1 import storePainIntensitiesForParticipant1
from storeWhatPulse import storeWhatPulse
from storeManicTime import storeManicTime
from storeManicTimeBlankScreen import storeManicTimeBlankScreen
from storeEyeRelatedActivitiesParticipant1 import storeEyeRelatedActivitiesParticipant1
from storeSportDataParticipant1 import storeSportDataParticipant1
from retrieve_mentalstate_participant1 import retrieve_mentalstate_participant1
from calculateCumulatedElevationGainMoves import retrieve_stored_CEG_moves

# Creation of the dataframe where everything will be stored
i = pd.date_range("2015-11-19", periods=2320, freq="1D")
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {
    "basisPeakSteps": empty,
    "fitbitCaloriesBurned": empty,
    "fitbitSteps": empty,
    "fitbitDistance": empty,
    "fitbitFloors": empty,
    "fitbitMinutesSedentary": empty,
    "fitbitMinutesLightlyActive": empty,
    "fitbitMinutesFairlyActive": empty,
    "fitbitMinutesVeryActive": empty,
    "fitbitActivityCalories": empty,
    "kneePain": empty,
    "handsAndFingerPain": empty,
    "fingersPain": empty,
    "foreheadAndEyesPain": empty,
    "forearmElbowPain": empty,
    "aroundEyesPain": empty,
    "shoulderNeckPain": empty,
    "sick_tired": empty,
    "painInOtherRegion": empty,
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
    "manicTimeBlankScreenC1": empty,
    "manicTimeBlankScreenC2": empty,
    "manicTimeBlankScreenC3": empty,
    "manicTimeBlankScreenT": empty,
    "manicTimeDelta": empty,
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
    "timeDrivingCar": empty,
    "scooterRiding": empty,
    "movesSteps": empty,
    "googlefitSteps": empty,
    "generalmood": empty,
    "elevation_gain": empty, # this will come from google fit
    "elevation_loss": empty, # this will come from google fit
    "calories": empty,       # this will come from google fit
    "climbingDenivelation": empty,
    "climbingMaxEffortIntensity": empty,
    "climbingMeanEffortIntensity": empty,
    "swimmingKm": empty,
}
data = pd.DataFrame(data=d, index=i)

print(data)

# Storing BasisPeak data in dataframe
if (True):  # This step takes a long time, put to False if you want to skip it, and to True otherwise
    filename = "../data/raw/ParticipantData/Participant1/bodymetrics.csv"
    data = storeBasisPeakInDataFrame(filename, data)

# Storing fitbit data in dataframe
fname = "../data/raw/ParticipantData/Participant1/dailyFitBitPerMonth/"
data = fitbitDataGatheredFromWebExport(fname, data)

# Storing moves data in dataframe
fname = "../data/raw/ParticipantData/Participant1/MovesAppData/daily/summary/"
data = movesDataGatheredFromWebExport(fname, data)

# Storing google fit data in dataframe
filename1 = "../data/raw/ParticipantData/Participant1/GoogleFitData/smartphone1/dailyAggregations/dailySummaries.csv"
data = googleFitGatheredFromWebExport(filename1, data, 13)

filename2 = "../data/raw/ParticipantData/Participant1/GoogleFitData/smartphone2/dailyAggregations/dailySummaries.csv"
data = googleFitGatheredFromWebExport(filename2, data, 13)

# Storing pain intensities in dataframe
filename = "../data/raw/ParticipantData/Participant1/pain.csv"
data = storePainIntensitiesForParticipant1(filename, data)

# Storing whatPulse data in dataFrame
fname = "../data/raw/ParticipantData/Participant1/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeWhatPulse(fname, numberlist, data)

# Storing Manic Time data in dataFrame
fname = "../data/raw/ParticipantData/Participant1/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeManicTime(fname, numberlist, data)

# Storing Manic Time Blank Screen data in dataframe
fname = "../data/raw/ParticipantData/Participant1/computerUsage/computer"
numberlist = ["1", "2", "3"]
data = storeManicTimeBlankScreen(fname, numberlist, data)

# Create Manic Time Delta Column in dataframe
data.loc['2022-03-27','manicTimeBlankScreenT'] = 0 # REMOVE THIS LATER!!!
data['manicTimeDelta'] = data['manicTimeT'] - data['manicTimeBlankScreenT'].astype(int)

# Storing Sport data in dataframe
filename = "../data/raw/ParticipantData/Participant1/sport.csv"
data = storeSportDataParticipant1(filename, data)

# Storing Eye related activity hours in dataframe
filename = "../data/raw/ParticipantData/Participant1/eyeRelatedActivities.csv"
data = storeEyeRelatedActivitiesParticipant1(filename, data)

# Storing mental states
filename = "../data/external/myaiguideconfidentialdata/Participant1/moodAndOtherVariables.csv"
data = retrieve_mentalstate_participant1(filename, data)

# Retrieving stored cumulated elevation gain from moves app
fname = "../data/raw/ParticipantData/Participant1/cum_gains_moves_participant1.csv"
data = retrieve_stored_CEG_moves(fname, data)

# Retrieve cumulated elevation gain from google fit app
fname = "../data/raw/ParticipantData/Participant1/GoogleFitData/smartphone1/Activités"
data = get_google_fit_activities(fname, data)
fname = "../data/raw/ParticipantData/Participant1/GoogleFitData/smartphone2/Activities"
data = get_google_fit_activities(fname, data)

# Saving the dataframe in a txt
output = open("../data/preprocessed/preprocessedDataParticipant1.txt", "wb")
pickle.dump(data, output)
output.close()
