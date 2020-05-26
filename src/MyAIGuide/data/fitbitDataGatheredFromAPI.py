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
from pandas.io.json import json_normalize


#%% 

def fitbitDataGatheredFromAPI(fname, data):
  
    """This function updates a dataframe with the JSON data
    gathered from the fitbit API 
    
    Params:
        fname: path to datafolder for participant X
        data:  pandas dataframe to store data
    
    """
    # Look for all json files in directory
    directory = os.fsencode(fname)
    
    for file in os.listdir(directory):
      name = os.fsdecode(file)
      
      if name.endswith("Fitbit.json"):
          file = (fname + name)
          
          # Open and load json into dataframe
          with open(file) as data_file:    
            jsondata = json.load(data_file) 
            
            df = json_normalize(jsondata, 'activities-steps')
        
            # Rename 'value' column to 'steps' 
            df = df.rename(columns={"value":"steps"})    
            
            # Set dateTime as time index
            df['dateTime'] = pd.to_datetime(df['dateTime'])
            df.set_index('dateTime', inplace=True)
            
            # Update empty dataframe with fitbit data from df
            data.update(df)

    return data
     