#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:17:52 2022

@author: corrado
"""

import numpy as np
import pandas as pd


from utils_funcs import set_dateTime



def extract_taplog(path_sport, path_taplog):
    """
    This function reads the files 'sport.csv' and TapLog2020_08_09until2022_07_30.csv,
    and cross-match them along time.

    Parameters
    ----------
    path_sport : string. It is the sport.csv file address
    path_taplog : It is the taplog file address

    Returns
    -------
    A pandas dataframe.

    """
######################
# read sport file
######################
    #data manipulation of sport.csv
    df_sport = pd.read_csv(path_sport, header=0,index_col=False)
    df_sport = df_sport[df_sport['start time'] != 'Garmin']
    df_sport = df_sport[df_sport['start time'] != 'Garmin/Fitbit']
    df_sport = df_sport[df_sport['start time'] != 'Fitbit']

#%%
    #fill missing 'taplog' in row
    #after that,  when 'start time' = 'taplog' then 'duration'='taplog too
    df_sport.loc[1967, 'start time'] = 'taplog'
    #drop line with peculiar activity ('preparing new mountain bike trail...')
    df_sport.drop(index=1641, inplace=True)


    #propagate year and months
    df_sport[['year','month']] = df_sport[['year','month']].ffill()
    #turn into str year, month, day
    
    df_sport[['year','month','day']] = df_sport[['year','month','day']].astype(int).astype(str)
    #format 'day'and month column
    df_sport['day'] = df_sport.day.apply(lambda x: '{:02d}'.format(int(x)))
    df_sport['month'] = df_sport.month.apply(lambda x: '{:02d}'.format(int(x)))
    #set date column
    df_sport['date'] = df_sport.apply(lambda row: row.year + '-' + row.month + '-' + row.day, axis=1)

    #drop lines that have NaN in "start time" and 'duration' (48 lines)
    df_sport.dropna(subset=['start time'], inplace=True)

    #set the "duration" column. assume that the values are expressed in minutes
    boole_taplog = (df_sport['start time'] == 'taplog') | (df_sport['duration'] == 'taplog')
    df_sport['taplog'] = boole_taplog


    #set the two new columns
    df_sport['startTimestamp'] = None
    df_sport['endTimestamp'] = None
    #put into the new columns the start and end time of the activity
    df_sport[['startTimestamp', 'endTimestamp']] = df_sport.apply(lambda row: pd.Series(set_dateTime(row)), axis=1)
#%%
    #some days the number of activities is higher than one. We need to handle it.
    #this will help us to match the activities with the taplog later.
    df_sport['activity_n'] = None
    #set a column that counts the number of activities reported per day
    for label, group in df_sport.date.groupby(by=df_sport.date):
        df_sport.loc[group.index,'activity_n'] = np.arange(len(group))
        
#%%
###############################
# read Taplog file
###############################
    #data manipulation of taplog
    if type(path_taplog) == list:
      for pathIdx, path_taplog_ in enumerate(path_taplog):
        if pathIdx == 0:
          df_taplog = pd.read_csv(path_taplog_, header=0, index_col=False)
        else:
          df_taplog_ = pd.read_csv(path_taplog_, header=0, index_col=False)
          df_taplog = pd.concat([df_taplog, df_taplog_], ignore_index=True)
    else:
      df_taplog = pd.read_csv(path_taplog , header=0,index_col=False)
    #select only these two columns
    cols2keep = ['timestamp','cat2']
    df_taplog = df_taplog[cols2keep].copy()
    #set the date
    df_taplog['date'] = df_taplog.timestamp.apply(lambda x: x[:10])
    
    #there are issues with 'sport str' and 'sport end' in the sense
    #there are cases in which for a start does not corresponf a "sport end"
    #and vice-versa. They are few cases. To make it short, I remove them.
    df_taplog['cat1'] = df_taplog.cat2.shift(-1)
    df_taplog['cat1'] = df_taplog['cat1'].ffill()
    #boolean that identify where cat1 and cat2 are equal
    boole_cat = (df_taplog.cat2 == df_taplog.cat1)
    #identify the dates that must be removed
    date_list = df_taplog.loc[boole_cat, 'date'].unique().tolist()
    date2remove = [True if x in date_list else False for x in df_taplog['date'].values.tolist()]
    idx2remove = df_taplog[np.array(date2remove)].index
    #remore them
    df_taplog.drop(idx2remove, inplace=True)
    #remove cat1, which is not useful anymore
    df_taplog.drop(columns='cat1', inplace=True)
    ###
    #
    #set the start and end timestamps
    df_taplog['endTimestamp'] = df_taplog.timestamp.shift(-1)
    df_taplog.rename(columns={'timestamp':'startTimestamp'}, inplace=True)
    #drop the 'Sport End' rows
    idx2drop = df_taplog[df_taplog.cat2 == 'Sport End'].index
    df_taplog.drop(index=idx2drop, inplace=True)
    df_taplog.drop(columns='cat2', inplace=True)

#%%
    #set a column that counts the number of activities reported per day
    #this is used later to match activities with taplogs
    df_taplog['activity_n'] = None

    for label, group in df_taplog.date.groupby(by=df_taplog.date):
        df_taplog.loc[group.index,'activity_n'] = np.arange(len(group))

    # NOTE: there are inconsistencies between sport and taplog, 
    # i.e. in date 2021-12-12 2 taplogs are reported but 3 sports

#%%
    #set indexes for merge
    df_taplog.set_index(['date','activity_n'], inplace=True)
    df_sport.set_index(['date','activity_n'], inplace=True)
    #merge the dataframes
    df_merged = df_taplog.merge(df_sport[['activity']], left_index=True, right_index=True)
    df_merged.reset_index(1, drop=True, inplace=True)

    return df_merged
