import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def storeSportDataParticipant1(filename, data):
  curYear = ""
  curMonth = ""
  curDay = ""
  with open(filename, newline="") as csvfile:
    spamreader = csv.reader(csvfile)
    count = 0
    for row in spamreader:
        count = count + 1
        if count > 1 and len(row):
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
            dict = {
                "Walk": "walk",
                "Road Bike": "roadBike",
                "Mt Bike": "mountainBike",
                "Swimming": "swimming",
                "Surfing": "surfing",
                "Climbing": "climbing",
                "Via Ferrata": "viaFerrata",
                "Alpi Ski": "alpiSki",
                "Down Ski": "downSki",
            }
            if row[3] in dict:
                data.loc[date, dict[row[3]]] = 1
            
            if row[3] == 'Climbing':
                try:
                    data.loc[date, 'climbingDenivelation'] = float(row[7])
                except:
                    data.loc[date, 'climbingDenivelation'] = 0
                try:
                    data.loc[date, 'climbingMaxEffortIntensity'] = float(row[13])
                except:
                    data.loc[date, 'climbingMaxEffortIntensity'] = 0
                try:
                    data.loc[date, 'climbingMeanEffortIntensity'] = float(row[15])
                except:
                    data.loc[date, 'climbingMeanEffortIntensity'] = 0

            if row[3] == 'Swimming':
                try:
                    data.loc[date, 'swimmingKm'] = float(row[6])
                except:
                    data.loc[date, 'swimmingKm'] = 0
                
  return data