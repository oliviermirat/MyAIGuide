import csv
import datetime
import os
import os.path
import pickle
import glob
import re

import numpy as np
import pandas as pd
import requests
from typing import List, Tuple

def get_cum_elevation_gain(elevations: List[float]) -> float:
    """
    Function that given the ordered sequence of elevation measurements during an
    activity, returns the total elevation gain.
    :param elevations: List of elevation measurements.
    :return: Cumulative elevation gain.
    """

    gain = 0

    if not elevations:
        return 0

    last_elevation = elevations[0]
    del elevations[0]

    for elevation in elevations:

        # signed increase within the last change
        delta = float(elevation) - float(last_elevation)

        # only add uphill change
        gain += max(delta, 0)

        # update last_elevation to current elevation
        last_elevation = elevation

    return gain


def get_date(fname):      
    
    # get filename
    directory = os.fsencode(fname)
    dateTime = []
    for file in os.listdir(directory):

        name = os.fsdecode(file)
        if name.endswith(".xml"):
            date = os.path.basename(name).split('.')[0]

            # date formatting 
            day = date[0:4]
            month = date[4:6]
            year = date[6:8]
            date = year + "-" + month + "-" + day
            dateTime.append(date)
    return dateTime


def get_gain(fname):      
    
    # get filename
    directory = os.fsencode(fname)
    gain = []
    for file in os.listdir(directory):
        name = os.fsdecode(file)
        if name.endswith(".xml"):
            filename = (fname + name)

            # extracts altitude and calculates elevation gain
            with open(filename, newline="") as csvfile:
                reader = csvfile.readlines()
                count = 0
                altitude = []
                for row in reader:
                    count = count + 1
                    if count > 6 and len(row): # remove the first 6 columns (definition)
                        df = row.split(',')
                        altitude.append(df[10])
                        altitude = [str(i).replace('"', '') for i in altitude]
                        altitude = [float(j) for j in altitude]
                altitude = [k for k in altitude if k > 1 and k < 10000] # select only plausible values 1m < k < 10000m
                altitude = altitude[:-2] # remove the second last columns (summary)

            altitude = get_cum_elevation_gain(altitude)
            gain.append(altitude)

    
    return gain  


def OruxTrace(data, fname):
    gain = get_gain(fname)
    date = get_date(fname)
    # load data into dataframe                
    df = pd.DataFrame(gain, columns= ['gain'])
                
    df['dateTime'] = pd.to_datetime(date)
    df.set_index('dateTime', inplace=True)

    # Update empty dataframe with OruxTrace data from df
    data.update(df)    

    return data