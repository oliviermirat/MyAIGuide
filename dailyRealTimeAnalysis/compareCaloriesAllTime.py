import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import sys
sys.path.insert(1, '../src/MyAIGuide/data')
from fitbitDataGatheredFromWebExport import fitbitDataGatheredFromWebExport
from processForBodyRegionHighlightParams import processForBodyRegionHighlightParams
from storeSportDataParticipant1 import storeSportDataParticipant1
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import json

figWidth  = 20
figHeight = 5.1

# Getting yesterday's date with Garmin data

with open("info.json", 'r') as json_file:
  info = json.load(json_file)

cnx = sqlite3.connect(info["pathToGarminSummaryDb"])
days_summary = pd.read_sql_query("SELECT * FROM days_summary", cnx)

yesterday_date = datetime.now() - timedelta(days=1)
yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")

if days_summary.loc[len(days_summary)-1, "day"] > yesterday_date_str:
  days_summary = days_summary[:len(days_summary)-1]

if days_summary.loc[len(days_summary)-1, "day"] < yesterday_date_str:
  yesterday_date_str = days_summary.loc[len(days_summary)-1, "day"]

# Getting Fitbit data

i = pd.date_range(start="2015-11-19", end=yesterday_date_str, freq="1D")
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
d = {
    "fitbitCaloriesBurned": empty,
    "fitbitSteps": empty,
    "fitbitDistance": empty,
    "fitbitFloors": empty,
    "fitbitMinutesSedentary": empty,
    "fitbitMinutesLightlyActive": empty,
    "fitbitMinutesFairlyActive": empty,
    "fitbitMinutesVeryActive": empty,
    "fitbitActivityCalories": empty,
    "swimming": empty,
    "surfing": empty,
    "calories": empty,
    "swimmingKm": empty,
    "mergedCalories": empty,
    "garminCalories": empty,
}
data = pd.DataFrame(data=d, index=i)

fname = "../data/raw/ParticipantData/Participant1/dailyFitBitPerMonth/"
data = fitbitDataGatheredFromWebExport(fname, data)
data["mergedCalories"] = data["fitbitCaloriesBurned"]

# Adding calories for surf and swim when they were not recorded

filename = "../data/raw/ParticipantData/Participant1/sport.csv"
data = storeSportDataParticipant1(filename, data)

dataAddSurfSwimCals = data.loc[data.index < "2022-07-12"].copy()

if True:
  for idx, val in enumerate(dataAddSurfSwimCals["surfing"]):
    if val:
      if str(dataAddSurfSwimCals.index[idx]) > "2018-07-25" and str(dataAddSurfSwimCals.index[idx]) < "2018-08-25":
        data["mergedCalories"][idx] += 200
      else:
        data["mergedCalories"][idx] += 400
  for idx, val in enumerate(dataAddSurfSwimCals["swimming"]):
    if val:
      data["mergedCalories"][idx] += 200

# Basis Peak

inputBasisPeak = open("basisPeakCalories.pkl", "rb")
dataBasisPeak = pickle.load(inputBasisPeak)
dataBasisPeak = dataBasisPeak.loc[dataBasisPeak.index <= "2016-12-31"]
inputBasisPeak.close()

data.loc[dataBasisPeak.index.tolist(), "basisPeakCalories"] = dataBasisPeak['basisPeakCalories'].tolist()
data.loc[dataBasisPeak.index.tolist(), "mergedCalories"]    = data.loc[dataBasisPeak.index.tolist(), "basisPeakCalories"]

data = data.loc[data.index >= "2015-12-25"]

# Merging garmin data with fitbit data

dataGarmin = pd.read_pickle('latestData.pkl') # latestData.pkl is created by the last run of 2_analyze.py
dataGarminSaved = dataGarmin.copy()
dataRecent = dataGarmin.loc[dataGarmin.index >= "2023-05-15"]

data.loc[dataRecent.index.tolist(), "garminCalories"] = (2000 + dataRecent['garminTotalActiveCalories']).tolist()
data.loc[dataRecent.index.tolist(), "mergedCalories"] = data.loc[dataRecent.index.tolist(), "garminCalories"]

# Preprocessing

for idx, val in enumerate(data["mergedCalories"]):
  if val < 1800:
    data["mergedCalories"][idx] = 2200 #data[idx-1]

# Rolling mean

data["CaloriesRollingMean"] = data["mergedCalories"].rolling(31).mean()

# Ploting

data[["mergedCalories", "CaloriesRollingMean"]].plot()
plt.show()


### Comparing calories data sources

from googleFitGatheredFromWebExport import googleFitGatheredFromWebExport
filename = "../data/raw/ParticipantData/Participant1/GoogleFitData/smartphone2/dailyActivityMetrics.csv"
data = googleFitGatheredFromWebExport(filename, data, 2)

dataBasisPeak['basisPeakCalories'].plot()
data["fitbitCaloriesBurned"].plot()
(2000 + dataGarminSaved["garminTotalActiveCalories"]).plot()
data['googlefitSteps'].plot()
plt.show()


# 

dataFitbitVsGoogle = data.loc[data.index >= "2022-07-15"].copy() #"2020-09-01"].copy()
dataFitbitVsGoogle = dataFitbitVsGoogle.loc[dataFitbitVsGoogle.index <= "2023-04-23"]
fitbitDivGoogle = (dataFitbitVsGoogle["fitbitCaloriesBurned"] / dataFitbitVsGoogle["googlefitSteps"]).mean()
print("fitbitDivGoogle:", fitbitDivGoogle)
dataGarminVsGoogle  = data.loc[data.index >= "2023-05-15"].copy()
dataGarminVsGoogle  = dataGarminVsGoogle.loc[dataGarminVsGoogle.index <= "2023-07-21"]
garminDivGoogle = (dataGarminVsGoogle['garminCalories'] / dataGarminVsGoogle["googlefitSteps"]).mean()
print("garminDivGoogle:", garminDivGoogle)
factor = fitbitDivGoogle / garminDivGoogle
print("factor:", factor)

dataFitbitVsBasisPeak  = data.loc[data.index >= "2016-09-05"].copy()
dataFitbitVsBasisPeak  = dataFitbitVsBasisPeak.loc[dataFitbitVsBasisPeak.index <= "2016-10-08"]
dataFitbitVsBasisPeak2 = data.loc[data.index >= "2016-10-15"].copy()
dataFitbitVsBasisPeak2 = dataFitbitVsBasisPeak2.loc[dataFitbitVsBasisPeak2.index <= "2016-12-30"]
dataFitbitVsBasisPeak  = pd.concat([dataFitbitVsBasisPeak, dataFitbitVsBasisPeak2])
dataFitbitVsBasisPeak  = dataFitbitVsBasisPeak.sort_index()
fitbitDivBasisPeak     = (dataFitbitVsBasisPeak['fitbitCaloriesBurned'] / dataFitbitVsBasisPeak["basisPeakCalories"]).mean()
print("fitbitDivBasisPeak:", fitbitDivBasisPeak)

# "factor" recalculation based on same day worned Fitbit vs Garmin:
# 29/02/2024: 2745/2534
factor2 = 2745/2534
factor3 = 2582/2457
# 23/03/2024:
factor4 = 2943/2566 # steps were: 17537/16005

# factor = np.mean([factor, factor2, factor3])
factor = np.mean([factor, factor2, factor3, factor4])
print("new factor calculation:", factor)

# choosing a more "conservative factor:
factor = 1.05
print("new factor calculation:", factor)

# Corrections based on estimates:

data.loc[data.index <= "2016-12-31", "mergedCalories"] = 1.05 * data.loc[data.index <= "2016-12-31", "mergedCalories"]
data.loc[data.index <= "2016-12-31", "CaloriesRollingMean"] = 1.05 * data.loc[data.index <= "2016-12-31", "CaloriesRollingMean"]

data.loc[data.index >= "2023-05-15", "mergedCalories"] = factor * data.loc[data.index >= "2023-05-15", "mergedCalories"]
data.loc[data.index >= "2023-05-15", "CaloriesRollingMean"] = factor * data.loc[data.index >= "2023-05-15", "CaloriesRollingMean"]

# data["basisPeakCalories"] = 1.05 * data["basisPeakCalories"]
# data.loc[dataBasisPeak.index.tolist(), "mergedCalories"]    = data.loc[dataBasisPeak.index.tolist(), "basisPeakCalories"]
# data["CaloriesRollingMean"] = data["mergedCalories"].rolling(31).mean()
data["meanCalories"] = data["mergedCalories"].mean()

data[["mergedCalories", "CaloriesRollingMean", "meanCalories"]].plot()

plt.show()
