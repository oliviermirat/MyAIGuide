import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def movesDataGatheredFromWebExport(fname, data):
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
                  if count > 1 and len(row):
                      dateMoves = re.split("/", row[0])
                      month = dateMoves[0]
                      day = dateMoves[1]
                      year = dateMoves[2]
                      if int(day) < 10:
                          day = "0" + str(day)
                      if int(month) < 10:
                          month = "0" + str(month)
                      year = "20" + year
                      date = year + "-" + month + "-" + day
                      if row[1] == "walking":
                          data.loc[date, "movesSteps"] = int(row[5])
  return data