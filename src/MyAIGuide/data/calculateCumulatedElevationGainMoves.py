#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:05:14 2020

@author: anniewong

[DESCRIPTION]
Functions to calculate cumulate elevation gain for the moves_export files 
(the .gpx files) from the confidential repos for participants 1 and 2. 
       
1. Retrieve gps coordinates and timestamp and store in dataframe
2. Group gps per day  
2. Retrieve elevation with Google API
3. Calculate cumulated elevation gain (CEG) per day
4. Combine CEV for running, cycling and walking into one dataframe, export to csv
5. Create function to update dataframe with CEG data

"""


#%% Imports
import pandas as pd
import gpxpy
import os
import logging
logging.getLogger().setLevel(logging.INFO)

try:
  import geo as geo
except ModuleNotFoundError:
  import src.MyAIGuide.data.geo as geo

#%% Retrieve data from GPX files and store in pandas dataframe

# CYCLING = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/cycling.gpx"
# RUNNING = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/running.gpx"
# WALKING = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/walking.gpx"

def gpx_to_dataframe(fname):
    
    """ This functions retrieves the lat, lon and timestamp 
    from a gpx file and returns it as a pandas dataframe
    
    params:
        fname: path to gpx file
        
    Return:
        df: pandas dataframe with the columns latitude, longitude, 
        elevation, time, lat_lon
    
    """
    
    # Open gpx file with gpxpy library
    gpx = gpxpy.parse(open(fname))
    
    # Initialize empty list to store data
    data = []
    
    # Get latitudem longitude and time 
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append([point.longitude, point.latitude,
                     point.elevation, point.time,])
    
    # Create dataframe
    columns = ['lon', 'lat', 'elevation', 'time']
    df = pd.DataFrame(data, columns=columns)
    #df.set_index('time', inplace=True)    
    df.time=pd.to_datetime(df.time)
    # add columns with tuple of lat lon
    df['lat_lon'] = df[['lat', 'lon']].apply(tuple, axis=1)
    
    return df

#cycling=gpx_to_dataframe(CYCLING)
#running=gpx_to_dataframe(RUNNING)
#walking=gpx_to_dataframe(WALKING)


#%% For each day, get list of tuples with lat/lon

def to_latlon_for_days(dataframe):
    
    """For each day get list of typles with lat lon that is needed
    for api call 
    
    params:
        dataframe: dataframe with colums lat, lon, time
        
    returns:
        dict(key:date, value: list of tuples with latlon)
    
    """
    
    result = dict()
    for index, row in dataframe.iterrows():
        row_date = str(row['time'].date())
        result[row_date] = result[row_date] + [row['lat_lon']] if row_date in result else [row['lat_lon']]
    return result

#cycling_daily=to_latlon_for_days(cycling)
#running_daily=to_latlon_for_days(running)
#walking_daily=to_latlon_for_days(walking)

#%% Get elevations from google api

def add_elevation_to_daily(data_daily: dict):
    
    """ Get elevation from google API 
    
    params:
        data_daily: dict(key:date, value: list of tuples with latlon)
    
    returns:
        list of tuples(date, (lat,lon), elevation)
    
    """
    
    result = []
    for day, daily_latlongs in data_daily.items():
        for daily_latlong in daily_latlongs:
            elevation = geo.get_elevation(locations=[daily_latlong], api_key=os.environ['GOOGLE_API_KEY'])[0]
            result.append((day, daily_latlong, elevation))
    return result

# result_cycling = add_elevation_to_daily(cycling_daily)
# result_walking = add_elevation_to_daily(walking_daily)
# result_running = add_elevation_to_daily(running_daily)

    
#%% Get cumulated elevation gain 

def get_cum_gain(apires):
    
    """Calculates cumulated elevation gain.
    
    Params:
        apires: list of tuples(date, (lat,lon), elevation)
    
    Returns a dataframe with date, list of elevation and cum gain
    
    """
    
    apires_df=pd.DataFrame(apires, columns=['date', 'latlon', 'elevation'])
    # Group elevations per day in a list
    get_daily= pd.DataFrame(apires_df.groupby('date')['elevation'].apply(list))
    # Calculate cum elevation gain 
    get_daily['cum_gain']=[geo.get_cum_elevation_gain(i) for i in get_daily.elevation]
    return get_daily

# cumgain_cycling=get_cum_gain(result_cycling)
# cumgain_walking=get_cum_gain(result_walking)
# cumgain_running=get_cum_gain(result_running)

#%% Get total dataframe with cumulated gains for participant 1 and 2 and export to folder

def export_cum_gain(cumgain_cycling=None, cumgain_walking=None, cumgain_running=None, filename="cum_gains_moves_participant.csv"):
    
    """ Combines the cumulated elevation gains dataframes (cycling, running, walking)  into one
    dataframe and exports it to a csv file"""

    # Rename columns
    cumgain_cycling.columns = ['elevation', 'cum_gain_cycling']
    cumgain_walking.columns = ['elevation', 'cum_gain_walking']
    
    # Participant2 does not have running data
    if cumgain_running==None:
            total_cumulated_elevation_gain = pd.concat([cumgain_cycling['cum_gain_cycling'], cumgain_walking['cum_gain_walking']], axis=1, sort=True)
    
    else:
        cumgain_running.columns = ['elevation', 'cum_gain_running']
        total_cumulated_elevation_gain = pd.concat([cumgain_cycling['cum_gain_cycling'], cumgain_walking['cum_gain_walking'], cumgain_running['cum_gain_running']], axis=1, sort=True)
    
    # Export 
    total_cumulated_elevation_gain.to_csv(filename, index=True)

#%%  Retrieve the cumulated elevation gains and add the data to a dataframe

def retrieve_stored_CEG_moves(fname, data):
  
    """This function updates a dataframe with the cumulated
    elevation gain (CEG) data from moves (for participant 1 and 2)
        
    Params:
        fpath: path to datafile with CEG data
        data:  pandas dataframe to store data
    
    Return:
        dataframe updated with cumulated elevation gains data from moves
        
    [NOTE] You can find the cumulated elevation gains dataframes here:
        CEV_PARTC1 = "./MyAIGuide/data/cumulatedElevationGainsMoves/Participant1/cum_gains_moves_participant1.csv"
        CEV_PARTC2 = "./MyAIGuide/data/cumulatedElevationGainsMoves/Participant1/cum_gains_moves_participant2.csv"        
    
    """
    # Read file
    cumulated_elevation_gains=pd.read_csv(fname, index_col=0)
    
    # Index as datetime index
    cumulated_elevation_gains.index=pd.to_datetime(cumulated_elevation_gains.index)
                
    # Update empty dataframe with CEV data from df (updates missing values)
    data.update(cumulated_elevation_gains)
    
    # Combine (updates new columns)
    res = data.combine_first(cumulated_elevation_gains)
            
    logging.info(f"Cumulated elevation gains from Moves added to dataframe")
            
    return res