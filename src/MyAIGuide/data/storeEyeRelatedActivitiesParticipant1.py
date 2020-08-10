import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def storeEyeRelatedActivitiesParticipant1(filename, data):
  curYear = ""
  curMonth = ""
  curDay = ""
  with open(filename, newline="") as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
        count = count + 1
        if count > 2 and len(row):
            if len(row[0]):
                curYear = row[0]
            if len(row[1]):
                curMonth = row[1]
                if len(curMonth) == 1:
                    curMonth = "0" + curMonth
            if len(row[2]):
                curDay = row[2]
                if len(curDay) == 1:
                    curDay = "0" + curDay
            date = curYear + "-" + curMonth + "-" + curDay
            tot = 0
            if len(row[3]):
                tot = tot + int(row[3])
            if len(row[4]):
                tot = tot + int(row[4])
            if len(row[5]):
                tot = tot + int(row[5])
            if len(row[7]):
                tot = tot + int(row[7])
            data.loc[date, "eyeRelatedActivities"] = tot
            if len(row[5]):
              data.loc[date, "timeDrivingCar"] = int(row[5])
              
            if len(row[9]):
                if len(row[10]):
                    data.loc[date, "scooterRiding"] = int(row[9]) + int(row[10])
                else:
                    data.loc[date, "scooterRiding"] = int(row[9])
            else:
                data.loc[date, "scooterRiding"] = 0
  return data