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
def compute_local_time(row, tf_object):
    #this function is used inside an "apply" function.
    #For each row identify the time zone and set the times as timestamp.
    #the times startTimestamp and endTimestamp appear to be UTC.
    #set the local times using the time zone
    lat = row.latitudeE7
    lon = row.longitudeE7
    str_tz = tf_object.timezone_at(lat=lat, lng=lon)
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
#####################################
def match_counts(df, df_counts, name_col):
    """
    This function cross-matches the df dataframe (containing the Google timeline)
    and files such as "steps" and "calories" (which belong to the fitbit data)
    in order to counts the number of steps and calories for each google timeline
    interval.

    Parameters
    ----------
    df : pandas dataframe that holds the Google timeline data
    df_counts : pandas dataframe that holds the counts of steps/calories/heart beat rate
    name_col : string that identify the column name that the counts will have 

    Returns
    -------
    The input pandas dataframe df updated with the added counts column

    """
    #iter through rows
    for idx,row in df.iterrows():
        #set lower boundary
        time_start = row.startTimestamp
        #set upper boundary
        time_end = row.endTimestamp
            
        boole, interval_type = set_interval_slice(df_counts, time_start, time_end)

        #pdb.set_trace()

        if interval_type == 'null': # this happen when the time interval in df_counts is before the first df time interval or after the last 
            continue # in this case, do nothing because the two intervals have no overlap
        elif interval_type == 'included':
            df_ = df_counts[boole].astype(float)
            df_['value_corr'] = df_.value
            time_frac = (time_end - time_start).total_seconds()/(df_.index[1] - df_.index[0]).total_seconds()
            df_['value_corr'].iloc[0] = df_['value'].iloc[0]*time_frac
            df_['value_corr'].iloc[1] = 0
        else:
            df_ = df_counts[boole].astype(float)
            df_['value_corr'] = df_.value
            time_start_frac = 1 - (time_start - df_.index[0]).total_seconds()/(df_.index[1] - df_.index[0]).total_seconds()
            time_end_frac = (time_end - df_.index[-2]).total_seconds()/(df_.index[-1] - df_.index[-2]).total_seconds()
            
            if interval_type == 'start_out':
                df_['value_corr'].iloc[-2] = df_['value'].iloc[-2]*time_end_frac
                df_['value_corr'].iloc[-1] = 0
            elif interval_type == 'end_out':
                df_['value_corr'].iloc[0] = df_['value'].iloc[0]*time_start_frac
                df_['value_corr'].iloc[-1] = 0
            elif interval_type == 'ordinary':
                df_['value_corr'].iloc[0] = df_['value'].iloc[0]*time_start_frac
                df_['value_corr'].iloc[-2] = df_['value'].iloc[-2]*time_end_frac
                df_['value_corr'].iloc[-1] = 0
            

            #sum up the number of steps between two consecutive timestamps of df
        df.loc[idx, name_col] = df_['value_corr'].sum()
            
    return df
###################
def set_interval_slice(df_counts, time_start, time_end):
    """
    This function return a boolean used to slice a time interval in df_counts with
    time_start and time_end as boundaries. It return also a string with the type of interval.

    Parameters
    ----------
    df_counts : pandas dataframe that holds the counts of steps/calories/heart beat rate
    time_start : upper time limit
    time_end : lower time limit

    Returns
    -------
    boole : boolean array with len(boole) = len(df_counts)
    interval_type: string
    """
    
    boole_low = df_counts.index < time_start
    boole_sup = df_counts.index > time_end
    
    #pdb.set_trace()
    #in case time_start and time_end are not covered by df_counts, set boole False everywhere
    if df_counts.index[-1] <= time_start or df_counts.index[0] >= time_end:
        idx_inf = len(df_counts) - 1
        idx_sup = 0
        interval_type = 'null'
    #otherwise...
    elif df_counts.index[0] > time_start and df_counts.index[0] < time_end: #if time_start is before the first steps info 
        idx_inf = 0 # set the first steps index
        idx_sup = np.where(boole_sup)[0][0] # pick the first true value
        interval_type = 'start_out'
    elif df_counts.index[-1] > time_start and df_counts.index[-1] < time_end: #if time_end is after the last steps info
        idx_inf = np.where(boole_low)[0][-1] # pick the last true value
        idx_sup = len(df_counts) -1 # set the last index
        interval_type = 'end_out'
    else:
        idx_inf = np.where(boole_low)[0][-1] # pick the last true value
        idx_sup = np.where(boole_sup)[0][0] # pick the first true value

        if idx_sup == idx_inf + 1:
            interval_type = 'included'
        else:
            interval_type = 'ordinary'

    #here we take the df_counts timestamp between time_start and time end
    boole = (df_counts.index >= df_counts.index[idx_inf]) & (df_counts.index <= df_counts.index[idx_sup])
    
    return boole, interval_type