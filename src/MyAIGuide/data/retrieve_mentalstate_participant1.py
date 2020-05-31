import csv
import datetime
import os
import os.path
import pickle
import re

import pandas as pd
import numpy as np

def retrieve_mentalstate_participant1(filename, data):
    """ Function updates a dataframe with mental state data for Participant 1

	fname: path to datafolder for participant 1
	data: pandas dataframe to store data
    """
	
    Year = ""
    Month = ""
    Day = ""
    with open(filename, newline="") as csvfile:
        csv_reader = csv.reader(csvfile)
        line_count = 0
        for i in csv_reader:
            line_count = line_count + 1
            if line_count > 1 and len(i):
                if len(i[0]):
                    Year = i[0]
                if len(i[1]):
                    Month = i[1]
                    if len(Month) == 1:
                        Month = "0" + Month
                if len(i[2]):
                    Day = i[2]
                    if len(Day) == 1:
                        Day = "0" + Day
                date = Year + "-" + Month + "-" + Day

                dict = {
                    "Really Good": 8,
                    "Good": 7,
                    "Fine": 6,
                    "Variable but mostly good": 5,
                    "Ok, but also not really that great": 4,
                    "Variable but mostly not great": 3,
                    "Tired": 2,
                    "Depressed": 1,  
                }

                if i[3] in dict:
                  data.loc[date, 'generalmood'] = dict[i[3]]

    return data
