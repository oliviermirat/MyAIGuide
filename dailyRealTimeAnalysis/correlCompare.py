from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import csv
import os
import re

def processForBodyRegionHighlightParams_ComputerToCaloriesCorrel(stressor1, data):

  scaler = MinMaxScaler()
  
  stressor1RollingMean = stressor1 + "_RollingMean"
  print("stressor1RollingMean:", stressor1RollingMean)

  data2 = data[[stressor1RollingMean, "manicTimeRealTime", "whatPulseRealTime"]].copy()
  
  data2 = data2[~data2.isin([np.nan, np.inf, 0]).any(axis=1)]
  
  data2["manicTimeRealTime"] = data2["manicTimeRealTime"].rolling(31).mean()
  data2["whatPulseRealTime"] = data2["whatPulseRealTime"].rolling(31).mean()
  
  data2 = data2[~data2.isin([np.nan, np.inf, 0]).any(axis=1)]
  
  data2[[stressor1RollingMean, "manicTimeRealTime", "whatPulseRealTime"]] = scaler.fit_transform(data2[[ stressor1RollingMean, "manicTimeRealTime", "whatPulseRealTime"]])

  data2[[stressor1RollingMean, "manicTimeRealTime", "whatPulseRealTime"]].plot()
  plt.show()

  x = data2[stressor1RollingMean].tolist()
  y = data2["manicTimeRealTime"].tolist()
  
  res = stats.pearsonr(x, y)
  print("1:", res)
  
  x = data2[stressor1RollingMean].tolist()
  y = data2["whatPulseRealTime"].tolist()
  res = stats.pearsonr(x, y)
  print("2:", res)



def compareCaloriesAllTime_ComputerToCaloriesCorrel(info, data, yesterday_date_str):

  ### Getting WhatPulse data

  pathToRealTimeWhatPulseList = info["pathToWhatPulseFolderList"]
  for pathToRealTimeWhatPulse in pathToRealTimeWhatPulseList:
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
            if date <= yesterday_date_str and date > '2015-12-25':
              if date < '2023-12-22' or date > '2023-12-29':
                data.loc[date, "whatPulseRealTime"] = int(row[1]) + int(row[2])
              else:
                data.loc[date, "whatPulseRealTime"] = int(row[1]) + int(int(row[1])/4) # some incorrect clicks where recorded from new glassouse click switch

  ### Getting manicTime data
  pathToRealTimeManicTimeList = info["pathToManicTimeUsageFileList"]
  for idx, pathToRealTimeManicTime in enumerate(pathToRealTimeManicTimeList):
    with open(pathToRealTimeManicTime, newline="") as csvfile:
      spamreader = csv.reader(csvfile)
      count = 0
      for row in spamreader:
        count = count + 1
        if count > 1 and len(row):
          if row[0][0:4] == "Acti":
            delimit = [m.start() for m in re.finditer("/", row[1])]
            if idx == 0:
              day = row[1][0 : delimit[0]]
              month = row[1][delimit[0] + 1 : delimit[1]]     
            else:
              month = row[1][0 : delimit[0]]
              day = row[1][delimit[0] + 1 : delimit[1]]
            if len(month) == 1:
              month = "0" + month
            if len(day) == 1:
              day = "0" + day
            year = row[1][delimit[1] + 1 : delimit[1] + 5]
            date = year + "-" + month + "-" + day
            hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
            if date <= yesterday_date_str and date > '2015-12-25':
              data.loc[date, "manicTimeRealTime"] += hours

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
          if date > "2023-11-11" and date <= yesterday_date_str:
            data.loc[date, "manicTimeRealTime"] += hours

  data["manicTimeRealTime"] = data["manicTimeRealTime"].rolling(31).mean()
  data["whatPulseRealTime"] = data["whatPulseRealTime"].rolling(31).mean()

  scaler = MinMaxScaler()
  data[["CaloriesRollingMean", "manicTimeRealTime", "whatPulseRealTime"]] = scaler.fit_transform(data[[ "CaloriesRollingMean", "manicTimeRealTime", "whatPulseRealTime"]])

  data[["CaloriesRollingMean", "manicTimeRealTime", "whatPulseRealTime"]].plot()

  plt.show()

  ###

  from scipy import stats

  data2 = data[["CaloriesRollingMean", "manicTimeRealTime", "whatPulseRealTime"]].copy()
  data2 = data2[~data2.isin([np.nan, np.inf, 0]).any(axis=1)]
  data2 = data2[(data2.index < '2020-03-01') | (data2.index > '2020-06-20')]

  data2[["CaloriesRollingMean", "manicTimeRealTime", "whatPulseRealTime"]].plot()
  plt.show()

  x = data2["CaloriesRollingMean"].tolist()
  y = data2["manicTimeRealTime"].tolist()
  res = stats.pearsonr(x, y)
  print("1:", res)

  x = data2["CaloriesRollingMean"].tolist()
  y = data2["whatPulseRealTime"].tolist()
  res = stats.pearsonr(x, y)
  print("2:", res)

  ###

  data3 = data2[data2.index > '2023-03-01']

  data3[["CaloriesRollingMean", "manicTimeRealTime", "whatPulseRealTime"]].plot()
  plt.show()

  x = data3["CaloriesRollingMean"].tolist()
  y = data3["manicTimeRealTime"].tolist()
  res = stats.pearsonr(x, y)
  print("1:", res)

  x = data3["CaloriesRollingMean"].tolist()
  y = data3["whatPulseRealTime"].tolist()
  res = stats.pearsonr(x, y)
  print("2:", res)
