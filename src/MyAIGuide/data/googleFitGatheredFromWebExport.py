import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def googleFitGatheredFromWebExport(filename1, filename2, data):
  with open(filename1, newline="") as csvfile:
      spamreader = csv.reader(csvfile)
      count = 0
      for row in spamreader:
          count = count + 1
          if count > 1 and len(row):
              dateMoves = re.split("-", row[0])
              year = dateMoves[0]
              month = dateMoves[1]
              day = dateMoves[2]
              date = year + "-" + month + "-" + day
              if len(row[13]):
                  data.loc[date, "googlefitSteps"] = int(row[13])
              else:
                  data.loc[date, "googlefitSteps"] = 0
                  
  with open(filename2, newline="") as csvfile:
      spamreader = csv.reader(csvfile)
      count = 0
      for row in spamreader:
          count = count + 1
          if count > 1 and len(row):
              dateMoves = re.split("-", row[0])
              year = dateMoves[0]
              month = dateMoves[1]
              day = dateMoves[2]
              date = year + "-" + month + "-" + day
              if len(row[10]):
                  data.loc[date, "googlefitSteps"] = int(row[10])
              else:
                  data.loc[date, "googlefitSteps"] = 0
  return data