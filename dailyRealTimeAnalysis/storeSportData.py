import csv
import datetime
import os
import os.path
import pickle
import re
from pyexcel_ods import get_data

import numpy as np
import pandas as pd

def storeSportData(filename, data):
    curYear = ""
    curMonth = ""
    curDay = ""

    # with open(filename, newline="") as csvfile:
      # spamreader = csv.reader(csvfile)
      
    dataFile = get_data(filename)
    # Assuming the first sheet; modify as per your data structure
    sheet_name = list(dataFile.keys())[0]
    rows = dataFile[sheet_name]
    
    count = 0
    for row in rows:
        count = count + 1
        if count > 1 and len(row):
            if type(row[0]) == int:
                curYear = row[0]
            if type(row[1]) == int:
                curMonth = row[1]
                if curMonth < 10:
                    curMonth = "0" + str(curMonth)
            if type(row[2]) == int:
                curDay = row[2]
                if curDay < 10:
                    curDay = "0" + str(curDay)
            date = str(curYear) + "-" + str(curMonth) + "-" + str(curDay)
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