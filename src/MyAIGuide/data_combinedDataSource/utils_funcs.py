#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 18:28:07 2022

@author: corrado
"""

import os
import numpy as np
import pandas as pd
import datetime as dt
import timezonefinder as tf
import time
##################################
def print_time(startTime, text):
    #this function just esteems the execution time for a particular cell.
    executionTime = (time.time() - startTime)
    hours = int(executionTime/3600)
    mins = int((executionTime - hours*3600)/60)
    secs = int(executionTime - hours*3600 - mins*60)
    print(text + ' execution time:' + str(hours) + 'h ' + str(mins)+ 'm '+ str(secs) + 's')
    return time.time()
####################################
def compute_local_time(row):
    #this function is used inside an "apply" function.
    #For each row identify the time zone and set the times as timestamp.
    #the times startTimestamp and endTimestamp appear to be UTC.
    #set the local times using the time zone
    lat = row.latitudeE7
    lon = row.longitudeE7
    str_tz = tf.TimezoneFinder().certain_timezone_at(lat=lat, lng=lon)
    startT = str(pd.Timestamp(row.startTimestamp, tz=str_tz).tz_localize(None))
    endT = str(pd.Timestamp(row.endTimestamp, tz=str_tz).tz_localize(None))

    return str_tz, startT, endT
########################################
def count_values(row, s_):
    """
    #this function is employed inside the match_counts function
    
    Parameters
    ----------
    row: it is a pandas dataframe's row
    s_: it is a pandas Series
    
    Returns
    -------
    n_steps: an integer
    
    """    

    time_up = row['endTimestamp'].round(freq='S')
    time_low = row['startTimestamp'].round(freq='S')
    boole = (s_.index>=time_low) & (s_.index<time_up)
    n_steps = s_[boole].sum()
    return n_steps
#%%
##########################################
def match_counts(df, df_counts, name_col):
    """
    This function has been written to cross-match the df dataframe and files 
    such as "steps", "calories", "heart beat rate". The first and the three lasts refers to
    different time intervals. Therefore, we here keep the df time intervals and counts the number
    of steps/calories/mean heart beat rate converting the latters as their mean per second.

    Parameters
    ----------
    df : pandas dataframe that holds the Google timeline data
    df_counts : the pandas dataframe that holds the counts of steps/calories/heart beat rate
    name_col : string that identify the column name that the counts will have 

    Returns
    -------
    The input pandas dataframe df updated with the added counts column

    """
    #iter through rows
    for idx,row in df.iterrows():
        #set lower boundary
        delta_time = dt.timedelta(seconds=60)
        time_low = row.startTimestamp - delta_time
        #set upper boundary
        time_up = row.endTimestamp + delta_time
        bool_time_df_counts = (df_counts.index >= time_low) & (df_counts.index <= time_up)

        #both df and df_counts must contain points. If not, do nothing.
        if bool_time_df_counts.sum()>0:
            #pdb.set_trace()
            #dd is a slice of df_counts
            dd = df_counts[bool_time_df_counts]
            #the next two lines create the series s_ containing the number of steps
            #per seconds between the days time_low and time_up
            s_ = dd.value.resample('s').asfreq().astype(float)
            s_ = s_.fillna(0).groupby(s_.notna().cumsum()).transform('mean')

            #pdb.set_trace()
            #sum up the number of steps between two consecutive timestamps of df
            df.loc[idx, name_col] = count_values(row,s_)
    return df
###############################
def set_dateTime(row):
    #function used inside an "apply" function
    #it set the start and end times of activities found 
    #inside df_sport
    
    day_string = row.date
    if not row.taplog:
        hour_string_start = row['start time']
        datetime_start = pd.Timestamp(day_string + ' ' + hour_string_start)

        delta_time = dt.timedelta(seconds=float(row.duration)*60)
        datetime_end = datetime_start + delta_time
    else:
        datetime_start = None
        datetime_end = None

    return datetime_start, datetime_end