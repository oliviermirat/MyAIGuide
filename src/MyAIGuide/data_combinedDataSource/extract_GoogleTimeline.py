#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 09:45:54 2022

@author: corrado
"""
import os
import numpy as np
import pandas as pd
import json
import datetime as dt
import timezonefinder as tf
import pdb

from utils_funcs import compute_local_time
####################################


def extract_googletimeline(path):

    #set the dataframe
    df = pd.DataFrame()
#%%
    #read the json file and put the extracted data into a dataframe
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path,dir_name)
        for file_name in os.listdir(dir_path):
            if file_name.endswith('.json'):# and file_name.startswith('2022_'):
                file_path = os.path.join(dir_path,file_name)
                with open(file_path, encoding="utf8") as data_file:
                    data = json.load(data_file)
                    df_ = pd.json_normalize(data['timelineObjects'], errors='ignore')
                    df = pd.concat([df, df_], ignore_index=True)

#%%
    #select the interesting "placevisit" columns 
    placevisits_cols = ['placeVisit.location.name', 'placeVisit.location.latitudeE7', 'placeVisit.location.longitudeE7',
                    'placeVisit.duration.startTimestamp', 'placeVisit.duration.endTimestamp', 
                    'placeVisit.placeVisitType', 'placeVisit.simplifiedRawPath.distanceMeters']
    #select the interesting "activitysegment" columns
    activitysegment_cols = ['activitySegment.duration.startTimestamp', 'activitySegment.duration.endTimestamp', 
       'activitySegment.distance', 'activitySegment.activityType', 'activitySegment.confidence', 
       'activitySegment.waypointPath.distanceMeters',
       'activitySegment.waypointPath.travelMode','activitySegment.waypointPath.confidence',
       'activitySegment.simplifiedRawPath.distanceMeters', 'activitySegment.startLocation.latitudeE7',
       'activitySegment.startLocation.longitudeE7']

    all_cols = placevisits_cols + activitysegment_cols

#%%
    #the placeVisit.placeVisitType and the activitySegment.activityType do not overlap in time
    #therefore we can extract them separately and later merge them into a single dataframe
    boole_visits = df['placeVisit.placeVisitType'].notnull()
    boole_activity = df['activitySegment.activityType'].notnull()
    #put them into two dataframes
    df_v = df.loc[boole_visits, placevisits_cols].copy()
    df_a = df.loc[boole_activity, activitysegment_cols].copy()
#%%
    #rename the columns in order to merge the two dataframes
    df_v.rename(columns={'placeVisit.location.name': 'Location',
                     'placeVisit.location.latitudeE7': 'latitudeE7',
                     'placeVisit.location.longitudeE7': 'longitudeE7',
                     'placeVisit.duration.startTimestamp': 'startTimestamp',
                     'placeVisit.duration.endTimestamp': 'endTimestamp',
                     'placeVisit.placeVisitType': 'InferredTravelMode',
                     'placeVisit.simplifiedRawPath.distanceMeters': 'SimplifiedDistanceMeters'}, inplace=True)
    df_a.rename(columns={'activitySegment.startLocation.latitudeE7':'latitudeE7',
                     'activitySegment.startLocation.longitudeE7': 'longitudeE7',
                     'activitySegment.duration.startTimestamp': 'startTimestamp',
                     'activitySegment.duration.endTimestamp': 'endTimestamp',
                     'activitySegment.distance': 'ActivityDistance',
                     'activitySegment.activityType': 'VisitActivityType',
                     'activitySegment.waypointPath.distanceMeters': 'WaypointDistance',
                     'activitySegment.waypointPath.confidence': 'WayPointConfidence',
                     'activitySegment.waypointPath.travelMode': 'InferredTravelMode',
                     'activitySegment.simplifiedRawPath.distanceMeters': 'SimplifiedDistanceMeters'}, inplace=True)
    df_a['Location'] = 'Journey'
#%%
    #concatenate the two dataframes
    df_final = pd.concat([df_v, df_a], ignore_index=True)
    #sort them by time
    df_final.sort_values(by='startTimestamp', inplace=True)
    #convert the latitude and longitude to decimal degrees 
    df_final['latitudeE7'] = df_final['latitudeE7']/10**7
    df_final['longitudeE7'] = df_final['longitudeE7']/10**7


    #timezonefinder object instance
    tfObject = tf.TimezoneFinder()
    #set the timezone, and the local times
    df_final[['timeZone','startTimeLocal','endTimeLocal']] = df_final.apply(lambda row: pd.Series(compute_local_time(row, tfObject)), axis=1)


#%%
    #drop columns
    df_final.drop(columns=['latitudeE7', 'longitudeE7'], inplace=True)
    #reset index
    df_final.reset_index(drop=True, inplace=True)

    return df_final