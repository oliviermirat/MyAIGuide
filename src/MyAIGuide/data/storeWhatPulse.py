import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def storeWhatPulse(fname, numberlist, data):

  for num in numberlist:
    nbFiles = len([name for name in os.listdir(fname + num + "/whatPulse/")])
    for i in range(1, nbFiles + 1):
      filename = (fname + num + "/whatPulse/whatpulse-input-history" + str(i) + ".csv")
      with open(filename, newline="") as csvfile:
        spamreader = csv.reader(csvfile)
        count = 0
        for row in spamreader:
          count = count + 1
          if count > 1 and len(row):
            date = row[0][0:10]
            data.loc[date, "whatPulseKeysC" + num] = int(row[1])
            data.loc[date, "whatPulseClicksC" + num] = int(row[2])
  
  data["whatPulseKeysT"] = data["whatPulseKeysC1"] + data["whatPulseKeysC2"] + data["whatPulseKeysC3"]
  data["whatPulseClicksT"] = data["whatPulseClicksC1"] + data["whatPulseClicksC2"] + data["whatPulseClicksC3"]
  data["whatPulseT"] = data["whatPulseKeysT"] + data["whatPulseClicksT"]
  
  return data
