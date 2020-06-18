#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:05:14 2020

@author: anniewong
"""
# ISSUE DESCRIPTION
#To solve this issue, you will need to use the solution proposed in issue #20 to get the elevation from GPS coordinates.
#The aim is to calculate the cumulated elevation gain for physical activities recorded by Moves for Participant 1 and Participant 2.
#For both of these participants, you will find the data inside the confidential repo (there's a zip file for both of those called "moves_export").
#For both participants, the gpx, georss and geojson folders contain the best information about gps coordinates.

# STEP 1: EXTRACT INFORMATION PER FOLDER (ues the file in the 'full' folder to get total instances)
### folders description
#### 1. GEOJSON ####
# Coordinates are stored in places.geojson. 
# Indicates how long one has stayed at a particular location 

#### GPX ####
# timestamps and coordinates of tracks
# A track consists of segments, segments consist of gps points

### GEORSS ###
# timestamps and coordinates of locations

# STEP 2: USE LAT/LON TO GET ELEVATION FROM GOOGLE API

#%% Import libraries
import pandas as pd
import geopandas as gpd
from pandas.io.json import json_normalize

import logging
logging.getLogger().setLevel(logging.INFO)

#%%  1. GEOJSON FOLDER (places.geojson)
# places.geojson files give the start and endtime of a location (lat/lon)

fname = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/geojson/full/places.geojson"


def places_geojson_to_dataframe(fname):
    
    """This function retrieves the starttime, endtime and the 
    lat/lon coordinates of a location from a places.geojson file 
    and returns it as a pandas dataframe
    
    params:
        fname: path to file
        
    return:
       df: pandas dataframe with the columns starttime, endtime, date, location.lat, 
        location.lon
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
    df.columns = ['startTime', 'endTime', 'date', 'latitude', 'longitude']
    
    return df


#%% GPX FOLDER 
    
import gpxpy
fname = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/gpx/full/places.gpx"

def gpx_to_dataframe(fname):
    
    """ This functions retrieves the lat,lon and timestamp from a gpx 
    file and returns it as a pandas dataframe
    
    params:
        fname: filename
        
    Return:
        df: pandas dataframe with the columns lat, lon, elevation and time
    
    """
    
    # Open gpx file with gpxpy library
    gpx = gpxpy.parse(open(fname))
    
    # Initialize empty list to store data
    data = []
    
    # How many tracks are there
    logging.info("Parsing {} track(s) from {}".format(len(gpx.tracks), fname))
    
    # Get latitudem longitude and time 
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append([point.longitude, point.latitude,
                     point.elevation, point.time,])
    
    # Create dataframe
    columns = ['Longitude', 'Latitude', 'Elevation', 'Time']
    df = pd.DataFrame(data, columns=columns)    
    
    return df


#%% GEORSS FOLDER

from bs4 import BeautifulSoup
fname = "../data/external/myaiguideconfidentialdata/Participant1/moves_export/georss/full/places.atom"

def georss_to_dataframe(fname):
    
    """This functions retrieves the lat,lon and time from a georss file 
    and returns it as a pandas dataframe 
    
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
    df[['lon', 'lat']] = df.location.str.split(expand=True)
    
    # drop location col
    df.drop('location', axis=1, inplace = True)
    
    return df
    

