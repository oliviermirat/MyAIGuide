#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:05:14 2020

@author: anniewong

[DESCRIPTION]
Functions to calculate cumulate elevation gain for the moves_export files 
from the confidential repos for participants 1 and 2.

[INFORMATION ABOUT FOLDERS]
For both participants, the geojson, gpx and georss folders contain the best 
information about gps coordinates. Read the files from the 'full' folder
to get the data for the total period.

Description per folder:
    - geojson: coordinates are stored in places.geojson
        indicates how long one has stayed at a particular location
      
    - gpx: coordinates are stored in places.gpx
        indicates the tracks of a person
        
    - georss: coordinates are stored in places.atom
        gives a lat/lon (location) along with timestamp
        
[TO DO LIST]
1a. Retrieve gps coordinates and timestamp and store in dataframe [DONE]
1b. merge all files from 1a
2. Using the gps coordinates, retrieve elevation with Google API
3. Calculate cumulated elevation gain

"""


#%% Imports
import pandas as pd
import geopandas as gpd
from pandas.io.json import json_normalize
import gpxpy
from bs4 import BeautifulSoup


#%%  1. GEOJSON: places.geojson

# fname = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/geojson/full/places.geojson"


def geojson_to_dataframe(fname):
    
    """This function retrieves the starttime, endtime and the 
    lat/lon of a location from places.geojson file 
    and returns it as a pandas dataframe
    
    params:
        fname: path to geojson file
        
    return:
       df: pandas dataframe with the columns starttime, endtime, date, 
       latitude and longitude
       
    """
    # Read file    
    df = gpd.read_file(fname)
    
    # Convert geodataframe to pandas dataframe
    df = pd.DataFrame(df)
    
    # Split 'place' column to separate variables and append to df
    df = pd.concat([df, json_normalize(df.place)], axis=1)
    
    # Parse starttime, endtime and date to datetime format
    df[['date','startTime', 'endTime']] = df[['date','startTime', 'endTime']].applymap(
            lambda x:pd.to_datetime(x))
    
    # Filter relevant columns
    df=df[['startTime', 'endTime', 'date', 'location.lat', 'location.lon']]
    
    # Rename
    df.columns = ['startTime', 'endTime', 'date', 'lat', 'lon']
    
    return df


#%% GPX: places.gpx

# fname = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/places.gpx"

def gpx_to_dataframe(fname):
    
    """ This functions retrieves the lat, lon and timestamp 
    from a gpx file and returns it as a pandas dataframe
    
    params:
        fname: path to gpx file
        
    Return:
        df: pandas dataframe with the columns latitude, longitude, 
        elevation and time
    
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
    
    return df


#%% GEORSS FOLDER: places.atomß

# fname = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/georss/full/places.atom"

def georss_to_dataframe(fname):
    
    """This functions retrieves the lat, lon and time from 
    a georss file and returns it as a pandas dataframe 
    
    params:
        fname: path to georss file
        
    return:
       df: pandas dataframe with the columns time, lon and lat 
    
    """

    handler=open(fname).read()
    soup=BeautifulSoup(handler)
    
    data = []
    
    results = soup.findAll('entry')
    for r in results:
        time = r.find('published').text
        coordinates = r.find('gml:pos').text
        data.append([time, coordinates])
    
    # Create dataframe
    columns = ['time', 'location']
    df = pd.DataFrame(data, columns=columns)
    
    # Split location into lat and lon (note:check if correct!)
    df[['lat', 'lon']] = df.location.str.split(expand=True)
    
    # Drop location col
    df.drop('location', axis=1, inplace = True)
    
    # Convert time column to datetime format
    df['time']=pd.to_datetime(df.time)
    
    return df
    

