import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def storePainIntensitiesForParticipant1(filename, data):
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
              dict = {
                  "Knees": "kneePain",
                  "Hands And Fingers": "handsAndFingerPain",
                  "Forehead and Eyes": "foreheadAndEyesPain",
                  "Forearm close to elbow": "forearmElbowPain",
                  "Eyes (or around them)": "aroundEyesPain",
                  "Shoulder Neck": "shoulderNeckPain",
              }
              if row[3] in dict:
                  data.loc[date, dict[row[3]]] = float(row[5])
  return data