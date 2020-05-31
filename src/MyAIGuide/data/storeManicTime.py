import csv
import datetime
import os
import os.path
import pickle
import re

import numpy as np
import pandas as pd

def storeManicTime(fname, numberlist, data):
  for num in numberlist:
      filename = (
          fname
          + num
          + "/manicTime/manicTime.csv"
      )
      with open(filename, newline="") as csvfile:
          spamreader = csv.reader(csvfile)
          count = 0
          for row in spamreader:
              count = count + 1
              if count > 1 and len(row):
                  if row[0][0:4] == "Acti":
                      if num == "1":
                          day = row[1][0:2]
                          month = row[1][3:5]
                          year = row[1][6:10]
                      else:
                          delimit = [m.start() for m in re.finditer("/", row[1])]
                          month = row[1][0 : delimit[0]]
                          day = row[1][delimit[0] + 1 : delimit[1]]
                          if len(month) == 1:
                              month = "0" + month
                          if len(day) == 1:
                              day = "0" + day
                          year = row[1][delimit[1] + 1 : delimit[1] + 5]
                      date = year + "-" + month + "-" + day
                      hours = int(row[3][0:1]) * 60 + int(row[3][2:4])
                      data.loc[date, "manicTimeC" + num] = (
                          data.loc[date, "manicTimeC" + num] + hours
                      )
  data["manicTimeT"] = data["manicTimeC1"] + data["manicTimeC2"] + data["manicTimeC3"]
  return data