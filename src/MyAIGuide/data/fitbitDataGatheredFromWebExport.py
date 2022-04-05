import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def fitbitDataGatheredFromWebExport(fname, data):
  directory = os.fsencode(fname)
  for file in os.listdir(directory):
      name = os.fsdecode(file)
      if name.endswith(".csv"):
          filename = (fname + name)
          with open(filename, newline="") as csvfile:
              spamreader = csv.reader(csvfile)
              count = 0
              for row in spamreader:
                  count = count + 1
                  if count > 2 and len(row):
                      day = row[0][0:2]
                      month = row[0][3:5]
                      year = row[0][6:10]
                      date = year + "-" + month + "-" + day
                      data.loc[date, "fitbitCaloriesBurned"]       = int(row[1].replace(",", ""))
                      data.loc[date, "fitbitSteps"]                = int(row[2].replace(",", ""))
                      data.loc[date, "fitbitDistance"]             = float(row[3].replace(",", "."))
                      data.loc[date, "fitbitFloors"]               = int(row[4])
                      data.loc[date, "fitbitMinutesSedentary"]     = int(row[5].replace(",", ""))
                      data.loc[date, "fitbitMinutesLightlyActive"] = int(row[6].replace(",", ""))
                      data.loc[date, "fitbitMinutesFairlyActive"]  = int(row[7].replace(",", ""))
                      data.loc[date, "fitbitMinutesVeryActive"]    = int(row[8].replace(",", ""))
                      data.loc[date, "fitbitActivityCalories"]     = int(row[9].replace(",", ""))
                      
  return data
