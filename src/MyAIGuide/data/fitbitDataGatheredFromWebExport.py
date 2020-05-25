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
                      data.loc[date, "steps"] = int(row[2].replace(",", ""))
                      data.loc[date, "denivelation"] = int(row[4])
  return data
