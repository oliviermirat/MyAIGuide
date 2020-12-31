import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def googleFitGatheredFromWebExport(filename, data, rowNumber):
  with open(filename, newline="") as csvfile:
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
                  data.loc[date, "googlefitSteps"] = int(row[rowNumber])
              else:
                  data.loc[date, "googlefitSteps"] = 0
  
  return data