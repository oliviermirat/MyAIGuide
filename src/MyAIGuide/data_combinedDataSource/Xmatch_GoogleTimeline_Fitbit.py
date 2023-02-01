#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 11:40:25 2022

@author: corrado
"""

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import pdb
import seaborn as sns
import pytz
import time

from extract_GoogleTimeline import extract_googletimeline
from extract_Fitbit import extract_fitbit
from utils_funcs import match_counts, print_time
from extract_TapLog import extract_taplog
#%%
####################################
#
# *** EDIT HERE THE NAMES AND PATHS OF THE FILES ***

path_timeline = 'MyAIGuide/data/external/myaiguideconfidentialdata/Participant1/GoogleTimeline/Semantic Location History/'

path_fitbit = 'MyAIGuide/data/external/myaiguideconfidentialdata/Participant1/MyFitbitData/logqs/Physical Activity/'


path_sport = 'MyAIGuide/data/raw/ParticipantData/Participant1/sport.csv'

path_taplog = 'MyAIGuide/data/raw/ParticipantData/Participant1/TapLog2020_08_09until2022_07_30.csv'

#name of the output file
file_pkl_out = '/MyAIGuide/data/preprocessed/googletimeline_fitbit.pkl'


#%%
#########################################################
startTime = time.time()

df = extract_googletimeline(path_timeline)

df['startTimestamp'] = pd.to_datetime(df['startTimestamp'], utc=True)
df['endTimestamp'] = pd.to_datetime(df['endTimestamp'], utc=True)
df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'], utc=False)
df['endTimeLocal'] = pd.to_datetime(df['endTimeLocal'], utc=False)
df['time_length'] = (df.endTimestamp - df.startTimestamp).dt.total_seconds()

startTime = print_time(startTime, 'timeline')

#this cell runs in ~20min
#%%
# this cell was useful for debugging
#df['endTimestamp-1'] = df.endTimestamp.shift(+1)
#df['delta_t'] = (df.startTimestamp - df['endTimestamp-1']).dt.total_seconds()
#verify that there are no overlapping time intervals
#assert (df.delta_t < 0).sum() == 0, "there are overlapping time intervals!"

#labels consecutive activity intervals
#df['delta_t'].fillna(0, inplace=True)
#df['activity_label'] = (~df.delta_t.duplicated(keep='last')).cumsum()
#%%
######################################

# find the cross-match with df_steps

######################################

#load the file
df_steps = extract_fitbit(path_fitbit,'steps')
df_steps.rename(columns={'dateTime':'timestamp'}, inplace=True)

df_steps['timestamp'] = pd.to_datetime(df_steps['timestamp'], utc=True)
df_steps.sort_values(by='timestamp', inplace=True)
df_steps.set_index('timestamp', drop=True, inplace=True)

startTime = print_time(startTime, 'steps')

df = match_counts(df, df_steps, 'steps_n')

startTime = print_time(startTime, 'merge steps')
#%%
#########################################

#          Xmatch with taplog

##########################################


#load the file
df_taplog = extract_taplog(path_sport, path_taplog)
df_taplog['startTimestamp'] = pd.to_datetime(df_taplog['startTimestamp'], utc=True)
#df_taplog.startTimestamp.apply(lambda x: pd.to_datetime(x).tz_convert('UTC'))
df_taplog['endTimestamp'] = pd.to_datetime(df_taplog['endTimestamp'], utc=True)
df_taplog.reset_index(inplace=True)

#there is 1 'Alpi ski' and one 'Down Ski'. Let's put it together
df_taplog['activity'].replace({'Alpi Ski': 'Ski', 'Down Ski':'Ski'}, inplace=True)
#replace 'Mt Bike' with 'cycling'
df_taplog['activity'].replace({'Mt Bike': 'Cycling'}, inplace=True)

for idx,row in df.iterrows():
    #set lower boundary
    time_start = row.startTimestamp
    #set upper boundary
    time_end = row.endTimestamp
    boole_taplog_end = (time_start < df_taplog.endTimestamp)
    boole_taplog_start = (time_end >= df_taplog.startTimestamp)
    boole_taplog = boole_taplog_end & boole_taplog_start

    if boole_taplog.sum() > 0:
        df_ = df_taplog[boole_taplog]
        for idx_,row_ in df_.iterrows():
            
            time_low = np.max([time_start, df_.startTimestamp.iloc[0]])
            time_up = np.min([time_end, df_.endTimestamp.iloc[0]])
            time_frac = (time_up - time_low)/(time_end - time_start)
            df.loc[idx,'taplog_activity'] = df_.loc[idx_,'activity']
            df.loc[idx,'time_activity_fraction'] = time_frac

    else:
        pass

startTime = print_time(startTime, 'merge taplog')
#%%

###########################################

# Xmatch with calories

###########################################

df_cal = extract_fitbit(path_fitbit,'calories')

df_cal.rename(columns={'dateTime':'timestamp'}, inplace=True)

df_cal['timestamp'] = pd.to_datetime(df_cal['timestamp'], utc=False)
df_cal.sort_values(by='timestamp', inplace=True)
df_cal.set_index('timestamp', drop=True, inplace=True)
#df_cal.rename(columns={'value':'calories'}, inplace=True)
df_cal['value'] = df_cal.value.astype(float)

#df_cal has time read in UTC. However, for unknown reasons, the
#time refers to the local time (instead of UTC). Therefore. to compare
#the time with df we must convert the time in tz-naive form with the following row
df_cal.index = df_cal.index.tz_localize(None)

#crate a dataframe with local time stamps in tz-naive form.
#then the dataframe df_ will be used to match calories and time
df_ = df[['startTimeLocal','endTimeLocal']].copy()
#rename the local time with 'startTimestamp' and 'endTimestamp' so that
#we can use the function match_counts
df_.rename(columns={'startTimeLocal':'startTimestamp', 'endTimeLocal': 'endTimestamp'}, inplace=True)
#the following function counts the number of calories
#for each time interval reported in df_
df_ = match_counts(df_, df_cal, 'calories')
df['calories'] = df_.calories


startTime = print_time(startTime, 'merge calories')
#%%
###########################################

# Xmatch with heart beat rate

###########################################

df_heart = extract_fitbit(path_fitbit,'heart_rate')
#df_heart contains bpm rate and also confidence values that span from 0 to 3.
#I could not find anywhere the meaning of this value scale. I here neglected it.

df_heart.rename(columns={'dateTime':'timestamp'}, inplace=True)
df_heart['timestamp'] = pd.to_datetime(df_heart['timestamp'], utc=True)
df_heart.sort_values(by='timestamp', inplace=True)

for idx,row in df.iterrows():
    #set lower boundary
    time_start = row.startTimestamp
    #set upper boundary
    time_end = row.endTimestamp
    boole_heart_end = (time_start < df_heart.timestamp)
    boole_heart_start = (time_end >= df_heart.timestamp)
    boole_heart = boole_heart_end & boole_heart_start

    if boole_heart.sum() > 0:
        heart_bpm_mean = df_heart.loc[boole_heart, 'value.bpm'].mean()
    else:
        heart_bpm_mean = np.nan
    df.loc[idx, 'meanHeartRate'] = heart_bpm_mean

startTime = print_time(startTime, 'merge heart')

#df_h = df_heart.tail(1000)


#%%
#drop useless columns and save
df.drop(columns=['time_length','startTimeLocal','endTimeLocal'], inplace=True)
#write it as pickle file
df.to_pickle(file_pkl_out)
