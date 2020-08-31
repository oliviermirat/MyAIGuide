import csv
from datetime import datetime
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
            date_from_name = re.split(".csv", re.split("_", name)[1])[0]
            year = date_from_name[0:4]
            month = date_from_name[4:6]
            day = date_from_name[6:8]
            date = datetime.strptime(year + "-" + month + "-" + day, '%Y-%m-%d')
            with open(filename, newline="") as csvfile:
                spamreader = csv.reader(csvfile)
                count = 0
                for row in spamreader:
                    count = count + 1
                    if count > 1 and len(row):
                        dateMoves = re.split("/", row[0])
                        if row[1] == "walking":
                            if row[1] == "walking":
                                data.loc[date, "movesSteps"] = int(row[5])
    return data
    