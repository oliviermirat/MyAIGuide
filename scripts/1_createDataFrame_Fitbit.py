#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 18:45:01 2020

@author: anniewong
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 10:21:46 2020

@author: anniewong
"""

#%% Import libraries
import os
import logging
logging.getLogger().setLevel(logging.INFO)
import json
import pandas as pd
from pandas.io.json import json_normalize

#%% Function to convert a single fitbit.json file to dataframe

def get_fitbit_dataframe(file):
    
    """This function takes as input a fitbit.json file and 
    returns the data as a pandas dataframe"""
    
    # Open and load json into dataframe             
    with open(file) as data_file:    
        data = json.load(data_file) 
        
    df = json_normalize(data, 'activities-steps')
    
    # Rename 'value' column to 'fitbitsteps' 
    df = df.rename(columns={"value":"fitbitsteps"})    
    
    return df
    

#%% Function to get all fitbit.json files in one dataframe
    
def get_all_fitbit_data_for_participants():
    
    """This function loops over all datafolders and returns 
    the fitbit.json files as one single dataframe with an extra column
    to indicate for the participant number"""

    # Path to data directory
    DATA_DIR = '../data/raw/ParticipantData/'
    
    # Initialize empty dataframe to store data
    dataframe = pd.DataFrame()
    
    # Loop over alle files in folders to find fitbit.json files 
    for subdir, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith("Fitbit.json"):
                
                fbfile = os.path.join(subdir, file)
                
                logging.info(f"Parsing {file}")
                
                # Open and load json into dataframe             
                with open(fbfile) as data_file:    
                    data = json.load(data_file)  
            
                df = json_normalize(data, 'activities-steps',)
                
                # Add  column to indicate participant number
                df.insert(loc=2, column="participant", value=file.replace(
                        "Fitbit.json", "")) 
                
                # Append data to master dataframe
                dataframe = dataframe.append(df)
    
    # Rename 'value' column to 'fitbitsteps' 
    dataframe = dataframe.rename(columns={"value":"fitbitsteps"})  
        
    logging.info(f"final dataframe has {len(dataframe)} rows and {len(dataframe.columns)} columns")
                
    return dataframe
            
    
    