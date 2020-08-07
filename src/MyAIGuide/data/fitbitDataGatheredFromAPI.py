#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 18:45:01 2020

@author: anniewong
"""

#%% Import libraries
import os
import json
import pandas as pd

import logging
logging.getLogger().setLevel(logging.INFO)

#%% 

def fitbitDataGatheredFromAPI(datadir, data):
  
    """This function updates a dataframe with the JSON data
    gathered from the fitbit API 
    
    Params:
        datadir: path to datafolder for participant X
        data:  pandas dataframe to store data
    
    Returns:
        dataframe data updated with fitbit API data
    
    """
    # Look for json files in directory
    for file in os.listdir(datadir):
        file = file.lower()
        if file.endswith("fitbit.json"):
          jsonfile = (datadir + file)
          
          logging.info(f"Parsing file '{file}' for fitbit data")
          
          # Open and load json into dataframe
          with open(jsonfile) as data_file:    
            jsondata = json.load(data_file) 
            
            df = pd.json_normalize(jsondata, 'activities-steps')
        
            # Rename 'value' column to 'steps' 
            df = df.rename(columns={"value":"steps"})    
            
            # Set dateTime as time index
            df['dateTime'] = pd.to_datetime(df['dateTime'])
            df.set_index('dateTime', inplace=True)
            
            # Automatically retrieve columns
            data=data.combine_first(df)
            
            # Update empty dataframe with fitbit data from df
            data.update(df)
            
            logging.info(f"Fitbit from API added to data")
            
    return data
     