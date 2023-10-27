import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import pickle

### Getting data

inputt = open('../data/preprocessed/fitbit_calories.pkl', "rb")
df_fitbit_calories = pickle.load(inputt)
inputt.close()

inputt = open('../data/preprocessed/fitbit_distance.pkl', "rb")
df_fitbit_distance = pickle.load(inputt)
inputt.close()

inputt = open('../data/preprocessed/fitbit_steps.pkl', "rb")
df_fitbit_steps = pickle.load(inputt)
inputt.close()

inputt = open('../data/preprocessed/fitbit_altitude.pkl', "rb")
df_fitbit_altitude = pickle.load(inputt)
inputt.close()

inputt = open('../data/preprocessed/taplog.pkl', "rb")
df_taplog = pickle.load(inputt)
inputt.close()

inputt = open('../data/preprocessed/fitbit_exercise.pkl', "rb")
df_fitbit_exercise = pickle.load(inputt)
inputt.close()
columnsNames = df_fitbit_exercise.columns.tolist().copy()
columnsNames[2] = columnsNames[2] + "_2" # This column's name is "duration" and as the name as another column
df_fitbit_exercise.columns = columnsNames

# Merging all the data coming from fitbit into a single dataframe

df_fitbit_calories['value']   = pd.to_numeric(df_fitbit_calories['value'], errors='coerce')
df_fitbit_distance['value']   = pd.to_numeric(df_fitbit_distance['value'], errors='coerce')
df_fitbit_steps['value']      = pd.to_numeric(df_fitbit_steps['value'], errors='coerce')
df_fitbit_altitude['value']   = pd.to_numeric(df_fitbit_altitude['value'], errors='coerce')
merged_df = pd.merge(df_fitbit_calories, df_fitbit_distance, on='dateTime', how='outer', suffixes=('_calories', '_distance'))
merged_df = pd.merge(merged_df, df_fitbit_steps, on='dateTime', how='outer', suffixes=('_distance', '_steps'))
merged_df = pd.merge(merged_df, df_fitbit_altitude, on='dateTime', how='outer', suffixes=('_steps', '_altitude'))
merged_df['dateTime'] = pd.to_datetime(merged_df['dateTime'])


### Cycling

# Creating dfCycling dataframe for which each line corresponds to a day when Participant 1 went cycling, adding total number of steps and cycling duration for each of those lines

taplogVsFitbitLogCutOff = "2022-07-15"

# Cycling from taplog
dfCycling = df_taplog[df_taplog['activity'] == "Mt Bike"].copy()
dfCycling = dfCycling[dfCycling.index <= taplogVsFitbitLogCutOff]

# Adding cycling session from fitbit logging to cyclying from taplog
df_fitbit_cycling = df_fitbit_exercise[(df_fitbit_exercise["activityName"] == "Vélo d'extérieur") | (df_fitbit_exercise["activityName"] == "Vélo")].copy()
df_fitbit_cycling = df_fitbit_cycling[df_fitbit_cycling["startTime"] > pd.to_datetime(taplogVsFitbitLogCutOff)]
df_fitbit_cycling.loc[df_fitbit_cycling["duration"] > 3.5*60*60*1000, "duration"] = 3*60*60*1000 # To remove outliers
df_fitbit_cycling['duration'] = pd.to_timedelta(df_fitbit_cycling['duration'], unit='ms')
df_fitbit_cycling['endTimestamp']   = df_fitbit_cycling['startTime'] + df_fitbit_cycling['duration']
df_fitbit_cycling['startTimestamp'] = df_fitbit_cycling['startTime']
df_fitbit_cycling['activity']       = "Mt Bike"
df_fitbit_cycling.index = pd.to_datetime(df_fitbit_cycling["startTime"]).dt.date
df_fitbit_cycling = df_fitbit_cycling[['startTimestamp', 'endTimestamp', 'activity']]
dfCycling = pd.concat([dfCycling, df_fitbit_cycling], axis=0)
dfCycling.index = [str(val) for val in dfCycling.index]

# Adding the total number of steps done during the cycling and the cycling duration
dfCycling["steps"] = 0.0
dfCycling["time"]  = 0.0
for i in range(len(dfCycling)):
  start_time = dfCycling.iloc[i]["startTimestamp"].tz_localize(None)
  end_time   = dfCycling.iloc[i]["endTimestamp"].tz_localize(None)
  df_fitbit_steps_duringBikeRide = df_fitbit_steps[(df_fitbit_steps['dateTime'] >= start_time) & (df_fitbit_steps['dateTime'] <= end_time)]
  df_fitbit_steps_duringBikeRide['value'] = pd.to_numeric(df_fitbit_steps_duringBikeRide['value'], errors='coerce')
  dfCycling.loc[dfCycling.index[i], "steps"] = np.sum(df_fitbit_steps_duringBikeRide["value"])
  dfCycling.loc[dfCycling.index[i], "time"]  = ((end_time - start_time).total_seconds()) / 60
  
# Outlier correction and saving data
dfCycling['stepsPerMinute'] =  dfCycling['steps']/dfCycling['time']
medianStepPerMinute = dfCycling.loc[dfCycling['stepsPerMinute']!=0, 'stepsPerMinute'].median()
dfCycling['stepsCorrected'] = dfCycling['steps'].copy()
dfCycling.loc[dfCycling['steps'] == 0, 'stepsCorrected'] = (medianStepPerMinute * dfCycling.loc[dfCycling['steps'] == 0, 'time']).astype('int')
print("medianStepPerMinute:", medianStepPerMinute)
dfCycling[['activity', 'steps', 'time', 'stepsPerMinute', 'stepsCorrected']].to_excel("cycling.xls")
path_output_file = '../data/preprocessed/cyclingStepsFromFitbit.pkl'
dfCycling[['activity', 'steps', 'time', 'stepsPerMinute', 'stepsCorrected']].to_pickle(path_output_file)


### Swimming

# Adding cycling session from fitbit logging to cyclying from taplog
df_fitbit_swimming = df_fitbit_exercise[df_fitbit_exercise["activityName"] == "Natation"].copy()
df_fitbit_swimming = df_fitbit_swimming[df_fitbit_swimming["startTime"] > pd.to_datetime(taplogVsFitbitLogCutOff)]
df_fitbit_swimming.loc[df_fitbit_swimming["duration"] > 4*60*60*1000, "duration"] = 4*60*60*1000 # To remove outliers
df_fitbit_swimming['duration'] = pd.to_timedelta(df_fitbit_swimming['duration'], unit='ms')
df_fitbit_swimming['endTimestamp']   = df_fitbit_swimming['startTime'] + df_fitbit_swimming['duration']
df_fitbit_swimming['startTimestamp'] = df_fitbit_swimming['startTime']
df_fitbit_swimming['activity']       = "Swimming"
df_fitbit_swimming.index = pd.to_datetime(df_fitbit_swimming["startTime"]).dt.date
df_fitbit_swimming = df_fitbit_swimming[['startTimestamp', 'endTimestamp', 'activity']]
df_fitbit_swimming.index = [str(val) for val in df_fitbit_swimming.index]

# Adding the total number of steps done during the cycling and the cycling duration
df_fitbit_swimming["steps"] = 0.0
df_fitbit_swimming["time"]  = 0.0
for i in range(len(df_fitbit_swimming)):
  start_time = df_fitbit_swimming.iloc[i]["startTimestamp"].tz_localize(None)
  end_time   = df_fitbit_swimming.iloc[i]["endTimestamp"].tz_localize(None)
  df_fitbit_steps_duringBikeRide = df_fitbit_steps[(df_fitbit_steps['dateTime'] >= start_time) & (df_fitbit_steps['dateTime'] <= end_time)]
  df_fitbit_steps_duringBikeRide['value'] = pd.to_numeric(df_fitbit_steps_duringBikeRide['value'], errors='coerce')
  df_fitbit_swimming.loc[df_fitbit_swimming.index[i], "steps"] = np.sum(df_fitbit_steps_duringBikeRide["value"])
  df_fitbit_swimming.loc[df_fitbit_swimming.index[i], "time"]  = ((end_time - start_time).total_seconds()) / 60
  
# Outlier correction and saving data
df_fitbit_swimming['stepsPerMinute'] =  df_fitbit_swimming['steps']/df_fitbit_swimming['time']
medianStepPerMinute = df_fitbit_swimming.loc[df_fitbit_swimming['stepsPerMinute']!=0, 'stepsPerMinute'].median()
df_fitbit_swimming['stepsCorrected'] = df_fitbit_swimming['steps'].copy()
df_fitbit_swimming.loc[df_fitbit_swimming['steps'] == 0, 'stepsCorrected'] = (medianStepPerMinute * df_fitbit_swimming.loc[df_fitbit_swimming['steps'] == 0, 'time']).astype('int')
print("medianStepPerMinute:", medianStepPerMinute)
df_fitbit_swimming[['activity', 'steps', 'time', 'stepsPerMinute', 'stepsCorrected']].to_excel("swimming.xls")
path_output_file = '../data/preprocessed/swimmingStepsFromFitbit.pkl'
df_fitbit_swimming[['activity', 'steps', 'time', 'stepsPerMinute', 'stepsCorrected']].to_pickle(path_output_file)


### Plotting for each day when cycling or swimming happenned

plotEachDayWhenCyclingHappened = True
plotEachDayWhenSwimmingHappened = True

if plotEachDayWhenCyclingHappened or plotEachDayWhenSwimmingHappened:

  # Adding cyclingHappening column to list of variables to plot
  df_fitbit_toPlot = merged_df.copy()
  df_fitbit_toPlot.index = df_fitbit_toPlot["dateTime"]
  df_fitbit_toPlot["cyclingHappening"] = 0
  for i in range(len(dfCycling)):
    start_time = dfCycling.iloc[i]["startTimestamp"].tz_localize(None)
    end_time   = dfCycling.iloc[i]["endTimestamp"].tz_localize(None)
    df_fitbit_toPlot["cyclingHappening"][(df_fitbit_toPlot['dateTime'] >= start_time) & (df_fitbit_toPlot['dateTime'] <= end_time)] = 100
  # Adding cyclingHappening column to list of variables to plot
  df_fitbit_toPlot["swimmingHappening"] = 0
  for i in range(len(df_fitbit_swimming)):
    start_time = df_fitbit_swimming.iloc[i]["startTimestamp"].tz_localize(None)
    end_time   = df_fitbit_swimming.iloc[i]["endTimestamp"].tz_localize(None)
    df_fitbit_toPlot["swimmingHappening"][(df_fitbit_toPlot['dateTime'] >= start_time) & (df_fitbit_toPlot['dateTime'] <= end_time)] = 100
  
  # Plotting of each cycling day
  
  if plotEachDayWhenCyclingHappened:
    
    for i in range(len(dfCycling)):
      
      # Selecting day when cycling happenned
      start_time = datetime.strptime(dfCycling.index[i], "%Y-%m-%d") #.tz_localize(None)
      end_time   = (start_time + timedelta(days=1)) #.tz_localize(None)
      df_fitbit_toPlot_Day = df_fitbit_toPlot[(df_fitbit_toPlot['dateTime'] >= start_time) & (df_fitbit_toPlot['dateTime'] <= end_time)].copy()
      print(i, start_time, end_time)
      
      # Scaling all values together if True just selection otherwise
      if False:
        scaler = MinMaxScaler()
        column_list = ["value_calories", "value_distance", "value_steps", "cyclingHappening", "swimmingHappening"]
        df_fitbit_toPlot_Day[column_list] = scaler.fit_transform(df_fitbit_toPlot_Day[column_list])
      else:
        column_list = ["value_steps", "cyclingHappening", "swimmingHappening"]
      df_fitbit_toPlot_Day = df_fitbit_toPlot_Day[column_list]
      
      # Plotting values
      fig, axes = plt.subplots(nrows=1, ncols=1)
      df_fitbit_toPlot_Day.plot(ax=axes)
      if True:
        plt.savefig("plot_" + start_time.strftime('%Y-%m-%d') + ".png")
      else:
        plt.show()

  # Plotting of each swimming day
  
  if plotEachDayWhenSwimmingHappened:
    
    for i in range(len(df_fitbit_swimming)):
      
      # Selecting day when cycling happenned
      start_time = datetime.strptime(df_fitbit_swimming.index[i], "%Y-%m-%d") #.tz_localize(None)
      end_time   = (start_time + timedelta(days=1)) #.tz_localize(None)
      df_fitbit_toPlot_Day = df_fitbit_toPlot[(df_fitbit_toPlot['dateTime'] >= start_time) & (df_fitbit_toPlot['dateTime'] <= end_time)].copy()
      print(i, start_time, end_time)
      
      # Scaling all values together if True just selection otherwise
      if False:
        scaler = MinMaxScaler()
        column_list = ["value_calories", "value_distance", "value_steps", "cyclingHappening", "swimmingHappening"]
        df_fitbit_toPlot_Day[column_list] = scaler.fit_transform(df_fitbit_toPlot_Day[column_list])
      else:
        column_list = ["value_steps", "cyclingHappening", "swimmingHappening"]
      df_fitbit_toPlot_Day = df_fitbit_toPlot_Day[column_list]
      
      # Plotting values
      fig, axes = plt.subplots(nrows=1, ncols=1)
      df_fitbit_toPlot_Day.plot(ax=axes)
      if True:
        plt.savefig("plot_swimming_" + start_time.strftime('%Y-%m-%d') + ".png")
      else:
        plt.show()
