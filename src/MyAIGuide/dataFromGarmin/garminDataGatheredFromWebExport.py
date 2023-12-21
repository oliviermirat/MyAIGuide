#%% Import libraries
import os
import json
import pandas as pd

def garminDataGatheredFromWebExport(datadir, data):
  
  # Look for json files in directory
  for file in os.listdir(datadir):
    if file.startswith("UDSFile_"):
      jsonfile = datadir + file
      # Open and load json into dataframe
      with open(jsonfile) as data_file:    
        jsondata = json.load(data_file) 
        df = pd.json_normalize(jsondata)
        
        # Rename 'value' column to 'steps' 
        df = df.rename(columns={"totalKilocalories":   "garminCalories"})
        df = df.rename(columns={"totalSteps":          "garminSteps"})
        df = df.rename(columns={"totalDistanceMeters": "garminDistance"})
        # Set dateTime as time index
        df['dateTime'] = pd.to_datetime(df['calendarDate'])
        df.set_index('dateTime', inplace=True)
        
        df = df[['garminCalories', 'garminSteps', 'garminDistance']]
        
        # Automatically retrieve columns
        data=data.combine_first(df)
        
        # Update empty dataframe with fitbit data from df
        data.update(df)
          
  return data



def garminActivityDataGatheredFromWebExport(datadir):
  
  # Look for json files in directory
  for file in os.listdir(datadir):
    if file.startswith("summarizedActivities"):
      jsonfile = datadir + file
      # Open and load json into dataframe
      with open(jsonfile) as data_file:    
        jsondata = json.load(data_file) 
        df = pd.json_normalize(jsondata[0]["summarizedActivitiesExport"])
        
        # Rename 'value' column to 'steps' 
        df = df.rename(columns={"activityType"  : "garminActivityType"})
        df = df.rename(columns={"sportType"     : "garminActivitySportType"})
        df = df.rename(columns={"distance"      : "garminActivityDistance"})
        df = df.rename(columns={"duration"      : "garminActivityDuration"})
        df = df.rename(columns={"elevationGain" : "garminActivityElevationGain"})
        df = df.rename(columns={"calories"      : "garminActivityCalories"})
        # Set dateTime as time index
        
        df['dateTime'] = pd.to_datetime(df['startTimeLocal'], unit='ms') #beginTimestamp'], unit='ms')
        # df.set_index('dateTime', inplace=True)
        
        # df = df[['garminActivityType', 'garminActivitySportType', 'garminActivityDistance', 'garminActivityDuration', 'garminActivityElevationGain', 'garminActivityCalories']]
          
  return df
