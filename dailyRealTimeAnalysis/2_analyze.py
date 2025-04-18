import sqlite3
import pandas as pd
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pyexcel_ods
import csv
import os
import re
import sys
sys.path.insert(1, '../src/MyAIGuide/dataFromGarmin')
from garminDataGatheredFromWebExport import garminDataGatheredFromWebExport, garminActivityDataGatheredFromWebExport
import json

with open("info.json", 'r') as json_file:
  info = json.load(json_file)

### Options

getDataFromGarminDb = True
garminDbStartDay    = "2023-12-18"

removeBlankScreenSaverTimes = True
addPhoneScreenTimes = True
includeCliffJumpingCalories = True
cliffJumpingActCaloPerMinute = 3.3 #2.7 # This might be a bit too conservative?

### Reloading data

inputt = open("../data/preprocessed/preprocessedMostImportantDataParticipant1.txt", "rb")

data = pickle.load(inputt)
inputt.close()


### Loading data from garmindb

cnx = sqlite3.connect(info["pathToGarminSummaryDb"])
days_summary = pd.read_sql_query("SELECT * FROM days_summary", cnx)

cnx = sqlite3.connect(info["pathToGarminActivitiesDb"])
activities   = pd.read_sql_query("SELECT * FROM activities", cnx)


### Get the current date and time

yesterday_date = datetime.now() - timedelta(days=1)
yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")

if days_summary.loc[len(days_summary)-1, "day"] > yesterday_date_str:
  days_summary = days_summary[:len(days_summary)-1]

if days_summary.loc[len(days_summary)-1, "day"] < yesterday_date_str:
  yesterday_date_str = days_summary.loc[len(days_summary)-1, "day"] # This might not be perfect (maybe just need to just update all data instead)

### Adding lines corresponding to unseen dates to the dataframe

new_dates = pd.date_range(start=data.index.max()+timedelta(days=1), end=yesterday_date_str)
new_data = pd.DataFrame(0, index=new_dates, columns=data.columns)
data = pd.concat([data, new_data])
data.sort_index(inplace=True)


### Adding new columns to the dataframe

new_columns = ['garminTotalActiveCalories', 'garminSurfSwimActiveCalories', 'garminClimbingActiveCalories', 'garminCyclingActiveCalories', 'garminBackcountrySkiingActiveCalories', 'garminCliffJumpingActiveCalories', 'garminKneeRelatedActiveCalories', 'garminArmsRelatedActiveCalories', 'garminSteps', 'whatPulseRealTime', 'manicTimeRealTime', 'realTimeKneePain', 'realTimeArmPain', 'realTimeFacePain', 'realTimeSick', 'realTimeOtherPain', 'realTimeEyeDrivingTime', 'realTimeEyeRidingTime', 'phoneTime'] #, 'garminDenivelationCyclingAndWalking', 'garminKneeRelatedDistanceAndDenivelation']
data[new_columns] = 0


### Getting the active calories per activity (cycling, surfswim and other/climbing) from web export ("old" data)

garminActivities = garminActivityDataGatheredFromWebExport(info["pathToGarminDataFromWebDIConnectFitness"])

garminCycling = garminActivities[garminActivities["garminActivityType"] == 'cycling'].copy() #['garminActivityDistance']
# garminCycling.index = garminCycling.index.strftime("%Y-%m-%d")
garminCycling["dateTime"] = garminCycling["dateTime"].apply(lambda x: x.strftime('%Y-%m-%d'))
garminCycling["activeCalories"] = (garminCycling["garminActivityCalories"] - garminCycling["bmrCalories"]) / 4.19002

garminSwimming = garminActivities[(garminActivities["garminActivityType"] == 'lap_swimming') | (garminActivities["garminActivityType"] == 'open_water_swimming') | (garminActivities["garminActivityType"] == 'surfing_v2')].copy()
# garminSwimming.index = garminSwimming.index.strftime("%Y-%m-%d")
garminSwimming["dateTime"] = garminSwimming["dateTime"].apply(lambda x: x.strftime('%Y-%m-%d'))
garminSwimming["activeCalories"] = (garminSwimming["garminActivityCalories"] - garminSwimming["bmrCalories"]) / 4.19002

garminOther = garminActivities[(garminActivities["garminActivityType"] == 'other') | (garminActivities["garminActivityType"] == 'rock_climbing')].copy()
# garminOther.index = garminOther.index.strftime("%Y-%m-%d")
garminOther["dateTime"] = garminOther["dateTime"].apply(lambda x: x.strftime('%Y-%m-%d'))
garminOther["activeCalories"] = (garminOther["garminActivityCalories"] - garminOther["bmrCalories"]) / 4.19002

cliffJumpingRows   = garminOther["activeCalories"] <= 0
garminCliffJumping = garminOther[cliffJumpingRows].copy()
garminCliffJumping['activeCalories'] = cliffJumpingActCaloPerMinute * (garminCliffJumping["elapsedDuration"] / (60 * 1000))
print("before cliff jumping removal:", len(garminOther))
garminOther = garminOther[~pd.Series(cliffJumpingRows)].reset_index(drop=True)
print("after cliff jumping removal:", len(garminOther))
print("cliff jumping number of rows:", len(garminCliffJumping))

groupedCycling  = garminCycling.groupby('dateTime')['activeCalories'].sum()
groupedSwimming = garminSwimming.groupby('dateTime')['activeCalories'].sum()
groupedOther    = garminOther.groupby('dateTime')['activeCalories'].sum()
groupedCliff    = garminCliffJumping.groupby('dateTime')['activeCalories'].sum()

groupedOther[groupedOther < 0] = 0 # is this still necessary?

data.loc[groupedCycling.index.tolist(), "garminCyclingActiveCalories"] = groupedCycling.values.tolist()
data.loc[groupedSwimming.index.tolist(), "garminSurfSwimActiveCalories"] = groupedSwimming.values.tolist()
data.loc[groupedOther.index.tolist(), "garminClimbingActiveCalories"]  = groupedOther.values.tolist()
data.loc[groupedCliff.index.tolist(), "garminCliffJumpingActiveCalories"]  = groupedCliff.values.tolist()

data.loc[days_summary["day"], 'garminSteps']               = days_summary["steps"].fillna(0).tolist()
data.loc[days_summary["day"], 'garminTotalActiveCalories'] = days_summary["calories_active_avg"].fillna(0).tolist()


# Getting the active calories per activity (cycling, surfswim and other/climbing) from garmindb (more recent data)

caloriesPerMinute = 2039 / (24 * 60)

previous_start_time = ""

if getDataFromGarminDb:
  print("")
  for i in range(len(activities)):
    start_time  = activities.loc[i, 'start_time']
    sport       = activities.loc[i, 'sport']
    if sport == "fitness_equipment":
      sport = activities.loc[i, 'sub_sport']
    calories    = activities.loc[i, 'calories']
    elapsedTime = activities.loc[i, 'elapsed_time']
    ascent      = activities.loc[i, 'ascent']  # Not taken into account cause everything related to GPS not so accurate
    descent     = activities.loc[i, 'descent'] # Not taken into account cause everything related to GPS not so accurate
    
    datetime_object = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
    start_time = datetime_object.strftime('%Y-%m-%d')
    
    if start_time >= garminDbStartDay and start_time <= yesterday_date_str:
      
      elapsedTime = datetime.strptime(elapsedTime, "%H:%M:%S.%f")
      hours   = elapsedTime.hour
      minutes = elapsedTime.minute
      seconds = elapsedTime.second
      elapsedTime = hours * 60 + minutes + seconds / 60
      
      calories = calories - caloriesPerMinute * elapsedTime

      if previous_start_time != start_time:
        print("")
      
      if sport == "generic" and activities.loc[i, 'name']:
        print("added from GarminDb: sport: ", sport, " ", activities.loc[i, 'name'].lower(), ", calories:", calories, ", start_time:", start_time, ", elapsedTime:", elapsedTime)
      else:
        print("added from GarminDb: sport: ", sport, ", calories:", calories, ", start_time:", start_time, ", elapsedTime:", elapsedTime)
      
      if sport == "cycling":
        data.loc[start_time, 'garminCyclingActiveCalories']  += calories
      elif sport == "swimming":
        data.loc[start_time, 'garminSurfSwimActiveCalories'] += calories
      elif sport == "other" or sport == "rock_climbing" or sport == "bouldering" or sport == "climbing" or sport == "generic":
        if includeCliffJumpingCalories and type(activities.loc[i, 'name']) == str and "cliff jumping" in activities.loc[i, 'name'].lower():
          data.loc[start_time, 'garminCliffJumpingActiveCalories'] += cliffJumpingActCaloPerMinute * elapsedTime
          print(data.loc[start_time, 'garminCliffJumpingActiveCalories'])
        elif type(activities.loc[i, 'name']) == str and "backcountry skiing" in activities.loc[i, 'name'].lower():
          print("adding backcountry skiing calories")
          data.loc[start_time, 'garminBackcountrySkiingActiveCalories'] += calories
        else:
          data.loc[start_time, 'garminClimbingActiveCalories'] += calories
      else:
        if sport != "walking":
          print("Activity not taken into account for calories:", sport)
      
      previous_start_time = start_time
      
  print("")


### Calculating garminKneeRelatedActiveCalories and garminArmsRelatedActiveCalories

data['garminKneeRelatedActiveCalories'] = data['garminTotalActiveCalories'] - data['garminSurfSwimActiveCalories'] - (data['garminClimbingActiveCalories'] * 0.75) + 0.5 * data['garminCliffJumpingActiveCalories'] - (data['garminBackcountrySkiingActiveCalories'] * 0.25)

data['garminArmsRelatedActiveCalories'] = data['garminSurfSwimActiveCalories'] + (data['garminClimbingActiveCalories'] * 0.75) + 0.1 * data['garminCyclingActiveCalories'] + 0.5 * data['garminCliffJumpingActiveCalories'] + (data['garminBackcountrySkiingActiveCalories'] * 0.25)

print("garminDbTotalActiveCalories", data['garminTotalActiveCalories'][len(data)-10:len(data)])


### Getting WhatPulse data

pathToRealTimeWhatPulse = info["pathToWhatPulseFolder"]
nbFiles = len([name for name in os.listdir(pathToRealTimeWhatPulse)])
for i in range(1, nbFiles + 1):
  filename = (pathToRealTimeWhatPulse + "whatpulse-input-history" + str(i) + ".csv")
  with open(filename, newline="") as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
      count = count + 1
      if count > 1 and len(row):
        date = row[0][0:10]
        if date <= yesterday_date_str:
          if date < '2023-12-22' or date > '2023-12-29':
            data.loc[date, "whatPulseRealTime"] = int(row[1]) + int(row[2])
          else:
            data.loc[date, "whatPulseRealTime"] = int(row[1]) + int(int(row[1])/4) # some incorrect clicks where recorded from new glassouse click switch


### Getting manicTime data

pathToRealTimeManicTime = info["pathToManicTimeUsageFile"]
with open(pathToRealTimeManicTime, newline="") as csvfile:
  spamreader = csv.reader(csvfile)
  count = 0
  for row in spamreader:
    count = count + 1
    if count > 1 and len(row):
      if row[0][0:4] == "Acti":
        delimit = [m.start() for m in re.finditer("/", row[1])]
        month = row[1][0 : delimit[0]]
        day = row[1][delimit[0] + 1 : delimit[1]]
        if len(month) == 1:
          month = "0" + month
        if len(day) == 1:
          day = "0" + day
        year = row[1][delimit[1] + 1 : delimit[1] + 5]
        date = year + "-" + month + "-" + day
        hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
        if date <= yesterday_date_str:
          data.loc[date, "manicTimeRealTime"] += hours


if removeBlankScreenSaverTimes:
  pathToRealTimeManicTime = info["pathToManicTimeAppFile"]
  with open(pathToRealTimeManicTime, newline="", encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
      count = count + 1
      if count > 1 and len(row) and row[0] == "Blank Screen Saver":
        delimit = [m.start() for m in re.finditer("/", row[1])]
        month = row[1][0 : delimit[0]]
        day = row[1][delimit[0] + 1 : delimit[1]]
        if len(month) == 1:
            month = "0" + month
        if len(day) == 1:
            day = "0" + day
        year = row[1][delimit[1] + 1 : delimit[1] + 5]
        date = year + "-" + month + "-" + day
        hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
        if date <= yesterday_date_str:
          data.loc[date, "manicTimeRealTime"] -= hours

if addPhoneScreenTimes:

  from calculate_daily_phone_usage import calculate_daily_phone_usage
  
  daily_usage = calculate_daily_phone_usage(info["pathToPhoneTimeFile"])
  
  if True:
    mean_last_7_days = daily_usage.tail(7)['Usage time'].mean()
    last_date = daily_usage["Date"].max()
    if isinstance(last_date, str):
      last_date = datetime.strptime(last_date, "%Y-%m-%d")
    new_dates = pd.date_range(start=last_date + timedelta(days=1), end=datetime.strptime(yesterday_date_str, '%Y-%m-%d'), freq='D')
    new_dates = new_dates.strftime("%Y-%m-%d")
    new_data = pd.DataFrame({
        "Date": new_dates,
        "Usage time": [mean_last_7_days] * len(new_dates)
    })
    daily_usage = pd.concat([daily_usage, new_data], ignore_index=True)
  
  for i in range(len(daily_usage)):
    date  = daily_usage["Date"][i]
    hours = daily_usage["Usage time"][i]
    if date <= yesterday_date_str:
      data.loc[date, "manicTimeRealTime"] += (hours/2)
      data.loc[date, "phoneTime"] = hours

goodComputerData = data[(data['manicTimeRealTime'] != 0) & (data['whatPulseRealTime'] != 0) & (~data['manicTimeRealTime'].isna()) & (~data['whatPulseRealTime'].isna())][['manicTimeRealTime', 'whatPulseRealTime']]
whatPulseByManicDividedAverage = (goodComputerData['whatPulseRealTime'] / goodComputerData['manicTimeRealTime']).mean()

whatPulseProblemData = data[(data['manicTimeRealTime'] != 0) & (data['whatPulseRealTime'] == 0) & (~data['manicTimeRealTime'].isna())]
data.loc[(data['manicTimeRealTime'] != 0) & (data['whatPulseRealTime'] == 0) & (~data['manicTimeRealTime'].isna()), "whatPulseRealTime"] = (whatPulseByManicDividedAverage * whatPulseProblemData["manicTimeRealTime"]).values.tolist()
# whatPulseProblemData["whatPulseRealTime"] = whatPulseByManicDividedAverage * whatPulseProblemData["manicTimeRealTime"]


### Overwritting WhatPulse and ManicTime data recorded after 28/11/2024 with custom made script
conn = sqlite3.connect(info["pathToCustomMadeClicksAndKeysMonitoringDB"])
cursor = conn.cursor()
cursor.execute("SELECT * FROM activity")
rows = cursor.fetchall()
for row in rows:
  date, keypresses, clicks, screen_on_time, nbAudioClicks = row
  if date >= '2024-11-28' and date <= yesterday_date.strftime('%Y-%m-%d'):
    data.loc[date, "manicTimeRealTime"] = screen_on_time / 60
    data.loc[date, "whatPulseRealTime"] = keypresses + clicks - nbAudioClicks



### Getting pain values

data1 = pyexcel_ods.get_data(info["pathToPainExcelFile"])
sheet_name = list(data1.keys())[0]
pain = pd.DataFrame(data1[sheet_name])

currentYear  = ''
currentMonth = ''
currentDay   = ''
for i in range(len(pain)):
  # Year
  if len(str(pain.loc[i, 0])):
    currentYear = pain.loc[i, 0]
  else:
    pain.loc[i, 0] = currentYear
  # Month
  if len(str(pain.loc[i, 1])):
    currentMonth = pain.loc[i, 1]
  else:
    pain.loc[i, 1] = currentMonth
  # Day
  if len(str(pain.loc[i, 2])):
    currentDay = pain.loc[i, 2]
  else:
    pain.loc[i, 2] = currentDay
  
  date = str(pain.loc[i, 0]) + "-" + str(pain.loc[i, 1]) + "-" + str(pain.loc[i, 2])
  
  if date in data.index:
    if type(pain.loc[i, 5]) == int or type(pain.loc[i, 5]) == float or type(pain.loc[i, 5]) == str:
      if pain.loc[i, 3] == "Knees":
        data.loc[date, "realTimeKneePain"] = float(pain.loc[i, 5])
      elif pain.loc[i, 3] in ["Hands And Fingers", "Fingers", "Forearm close to elbow", "Shoulder Neck", "Shoulder", "Elbow"]:
        data.loc[date, "realTimeArmPain"] = max(data.loc[date, "realTimeArmPain"], float(pain.loc[i, 5]))
      elif pain.loc[i, 3] in ["Forehead and Eyes", "Eyes (or around them)", "Eyes", "Forehead"]:
        data.loc[date, "realTimeFacePain"] = max(data.loc[date, "realTimeFacePain"], float(pain.loc[i, 5]))
      elif pain.loc[i, 3] in ["Sick", "Sick/Tired"]:
        data.loc[date, "realTimeSick"] = max(data.loc[date, "realTimeSick"], float(pain.loc[i, 5]))
      else:
        data.loc[date, "realTimeOtherPain"] = max(data.loc[date, "realTimeOtherPain"], float(pain.loc[i, 5]))

### Getting realTimeEyeDrivingTime value

data2 = pyexcel_ods.get_data(info["pathGeneralActiviesExcelFile"])
sheet_name = list(data2.keys())[0]
eyeRelated = pd.DataFrame(data2[sheet_name])

currentYear  = ''
currentMonth = ''
currentDay   = ''
for i in range(len(eyeRelated)):
  # Year
  if len(str(eyeRelated.loc[i, 0])):
    currentYear = eyeRelated.loc[i, 0]
  else:
    eyeRelated.loc[i, 0] = currentYear
  # Month
  if len(str(eyeRelated.loc[i, 1])):
    currentMonth = eyeRelated.loc[i, 1]
  else:
    eyeRelated.loc[i, 1] = currentMonth
  # Day
  if len(str(eyeRelated.loc[i, 2])):
    currentDay = eyeRelated.loc[i, 2]
  else:
    eyeRelated.loc[i, 2] = currentDay
  
  date = str(eyeRelated.loc[i, 0]) + "-" + str(eyeRelated.loc[i, 1]) + "-" + str(eyeRelated.loc[i, 2])
  
  if date in data.index:
    if type(eyeRelated.loc[i, 5]) == int or type(eyeRelated.loc[i, 5]) == float or (type(eyeRelated.loc[i, 5]) == str and len(eyeRelated.loc[i, 5])):
      try:
        data.loc[date, "realTimeEyeDrivingTime"] = float(eyeRelated.loc[i, 5])
      except:
        justToPutSomethingInExcept = 0
        # print("probably couldn't convert:", eyeRelated.loc[i, 5])
    if type(eyeRelated.loc[i, 7]) == int or type(eyeRelated.loc[i, 7]) == float or (type(eyeRelated.loc[i, 7]) == str and len(eyeRelated.loc[i, 7])):
      try:
        data.loc[date, "realTimeEyeRidingTime"] = float(eyeRelated.loc[i, 7])
      except:
        justToPutSomethingInExcept = 0
        # print("probably couldn't convert:", eyeRelated.loc[i, 7])


### Fixing missing pain value for specific day + making high pain values more "flat"

data.loc["2023-10-07", "realTimeKneePain"] = data["realTimeKneePain"]["2023-10-06"]
data.loc["2023-10-07", "realTimeArmPain"]  = data["realTimeArmPain"]["2023-10-06"]
data.loc["2023-10-07", "realTimeFacePain"] = data["realTimeFacePain"]["2023-10-06"]

data.loc[data["realTimeKneePain"] > 3.5, "realTimeKneePain"] = 3.5


### Store sport data

from storeSportData import storeSportData

data["surfing"] = 0
data["swimming"] = 0
data['climbingDenivelation'] = 0
data['climbingMaxEffortIntensity'] = 0
data['swimmingKm'] = 0
data['surfing'] = 0
data['cycling'] = 0
data['roadBike'] = 0
data['mountainBike'] = 0

data = storeSportData(info["pathToSportOdsFile"], data)

data["cycling"] = data["roadBike"] + data["mountainBike"]


### Saving processed data in pickle file

data.to_pickle('latestData.pkl')
