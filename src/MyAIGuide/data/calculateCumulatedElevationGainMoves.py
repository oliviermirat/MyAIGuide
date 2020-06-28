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
3. Calculate cumulated elevation gain per day

"""


#%% Imports
import pandas as pd
import gpxpy
import os

import MyAIGuide.data.geo as geo

#%% GPX: places.gpx

CYCLING = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/cycling.gpx"
RUNNING = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/running.gpx"
WALKING = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/walking.gpx"

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

#result_cycling = add_elevation_to_daily(cycling_daily)
#result_walking = add_elevation_to_daily(walking_daily)
#result_running = add_elevation_to_daily(running_daily)

    
#%% Get cumulated elevation gain 

def get_cum_gain(apires):
    
    """Calculates cumulate elevation gain.
    
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