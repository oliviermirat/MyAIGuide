#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 27 09:39:05 2020

@author: anniewong
"""

#%% Import libraries
import os
import pandas as pd
import datetime

import logging
logging.getLogger().setLevel(logging.INFO)

#%%

def storePainIntensitiesForParticipants2to9(datadir, data):
    
    """This function updates a dataframe with the pain intensities
    data for participants 2 to 9.
    
    Params:
        datadir: path to datafolder for participant X
        data:  pandas dataframe to store data 
        
    Returns:
        data: dataframe data updated with pain intensities
        """

    # Look for all Pain.csv files in directory
    for file in os.listdir(datadir):
      if file.endswith("Pain.csv"):
          painfile = (datadir + file)
          
          logging.info(f"Parsing file '{file}' for pain intensities")
          
          # Read pain.csv as pandas dataframe
          df = pd.read_csv(painfile)
          
          # The date columns are not accurate for participant8, use the 'date' column minus 1 day to retrieve date
          if file == 'Participant8Pain.csv':
              df['ndate'] = pd.to_datetime(df['date']) - pd.DateOffset(1)
              
          # For the rest of the participants, create date column from 'startyear', 'startmonth' and 'startday' 
          else:  
              df['ndate']=df.apply(lambda x: datetime.date(x['startyear'], x['startmonth'], x['startday']), axis=1)
            
          # Pivot 
          df = df.pivot_table(values='intensity', index=df.ndate, columns='name', aggfunc='first')
          df.index= pd.DatetimeIndex(df.index).normalize()
          
          # Resample at day level to correct data for participant8 as some dates occur multiple time in index
          df = df.resample('D').mean()
          
          # clean df.columns for merging with data
          df.columns = [col.lower().replace(' ','') for col in df.columns]
          
          # Join data with pain intensities dataframe
          data.columns = [col.lower().replace(' ', '') for col in data.columns]
          
          # Update data with values from df (automatically combines columns)
          data=data.combine_first(df)
              
          logging.info(f"Pain intensities added to data")
    
    return data