import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import pdb
import datetime

def selectColumns(data, columnList):
    data2 = data[columnList]
    return data2

def subset_period(data, start_period, end_period):
    """This function subsets a dataframe with datetime index
    within a time period

    Params:
        data: original dataframe
        start_period: start date of the period to subset
        end_period: end date of the period to subset

    """
    data2 = data.loc[data.index >= start_period].copy()
    return data2.loc[data2.index <= end_period]


def insert_rolling_mean_columns(data, column_list, window):
    """This function selects the columns of a dataframe
    according to a provided list of strings, re-scales its
    values and inserts a new column in the dataframe with the
    rolling mean of each variable in the column list and the
    provided window length.

    Params:
        data: original dataframe
        column_list: list of columns to select
        window: window length to calculate rolling mean

    """

    scaler = MinMaxScaler()
    data[column_list] = scaler.fit_transform(data[column_list])
    for var in column_list:
        data[var + "_RollingMean"] = data[var].rolling(window).mean()
    return data


def insert_relative_values_columns(data, column_list, short_window, long_window):
    """This function selects the columns of a dataframe
    according to a provided list of strings and inserts a new
    column in the dataframe with the ratio of the rolling_median wrt
    a short window divided by the rolling_median wrt a longer window.

    Params:
        data: original dataframe
        column_list: list of columns to select
        short_window: window length to calculate rolling median for the nummerator
        long_window: window length to calculate rolling median for the denominator

    """

    for var in column_list:
        var_short_window_rmedian = data[var].rolling(short_window).median()
        var_long_window_rmedian = data[var].rolling(long_window).median()
        relative_var_name = var + "_relative_" + str(short_window) + "_" + str(long_window)
        data[relative_var_name] = var_short_window_rmedian / var_long_window_rmedian

    return data


def addInsultIntensityColumns(data, columnList, window, windowMaxInsultDiff):
    scaler = MinMaxScaler()
    data[columnList] = scaler.fit_transform(data[columnList])

    for var in columnList:
        data[var + "InsultIntensity"] = (
            data[var].rolling(window).mean().shift(periods=1)
        )
        for i in range(0, window):
            data[var + "InsultIntensity"][i] = 0

    for var in columnList:
        data[var + "MaxInsultDiff"] = (
            data[var + "InsultIntensity"]
            .rolling(windowMaxInsultDiff)
            .min()
            .shift(periods=1)
        )
        for i in range(0, windowMaxInsultDiff):
            data[var + "MaxInsultDiff"][i] = 0
        data[var + "MaxInsultDiff"] = (
            data[var + "InsultIntensity"] - data[var + "MaxInsultDiff"]
        )

    return data


def getPainAboveThreshold(data, columnName, painThresh):
    data[columnName + "Threshed"] = data[columnName]
    for i in range(1, len(data) - 1):
        if float(data[columnName][i]) >= painThresh and (
            float(data[columnName][i - 1]) >= painThresh
            or float(data[columnName][i + 1]) >= painThresh
        ):
            data[columnName + "Threshed"][i] = 1
        else:
            data[columnName + "Threshed"][i] = 0
    data[columnName + "Threshed"][0] = 0
    data[columnName + "Threshed"][len(data) - 1] = 0
    return data


def getInsultAboveThreshold(data, columnName, thres2):
    data[columnName + "Threshed"] = data[columnName]
    for i in range(1, len(data) - 1):
        if float(data[columnName][i]) >= thres2["kneePain"][i]:
            data[columnName + "Threshed"][i] = 1
        else:
            data[columnName + "Threshed"][i] = 0
    return data


def check_if_zero_then_adjust_var_and_place_in_data(period, data, var_to_adjust_name, main_var_name, adjusted_var_name):
    df = data.copy()
    start_date = period[0]
    end_date = period[1]
    period_df = subset_period(df, start_date, end_date)

    var_to_adjust = period_df[var_to_adjust_name].values.reshape(-1, 1)
    main_var = period_df[main_var_name].values.reshape(-1, 1)
    
    dd = main_var/var_to_adjust
    dd = dd[np.logical_not(np.isnan(dd))]
    dd = dd[np.logical_not(np.isinf(dd))]
    dd = dd[np.logical_not(dd == 0)]
    medianValue = np.median(dd)
    print("medianValue:", medianValue)

    minVal = (np.median(main_var)) / 15
    
    final_data = [medianValue * var_to_adjust[idx] if mv < minVal and var_to_adjust[idx] != 0 else mv for idx, mv in enumerate(main_var)]
    print([(mv.tolist(), medianValue * var_to_adjust[idx], (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=int(idx))).strftime("%m/%d/%Y")) for idx, mv in enumerate(main_var) if mv < minVal and var_to_adjust[idx] != 0])
    data[adjusted_var_name][pd.date_range(start=start_date, end=end_date)] = np.transpose(final_data).tolist()[0]

    return [data, medianValue]


def predict_values(period, data, var_to_adjust_name, adjusted_var_name, medianValue):

    df = data.copy()
    # define start and end date of the period
    start_date = period[0]
    end_date = period[1]

    # subset the meaningful variables within period
    period_df = subset_period(df, start_date, end_date)

    var_to_adjust = period_df[var_to_adjust_name].values.reshape(-1, 1)
    # main_var = period_df[main_var_name].values.reshape(-1, 1)

    # Fit Linear Regression with:
    # X=var_to_adjust, Y=main_var
    # reg = LinearRegression().fit(var_to_adjust, main_var)

    # Calculate pred = reg.coef_*X + reg.intercept_
    # pred = reg.predict(var_to_adjust)
    pred = medianValue * var_to_adjust

    # Update the period adjusted_var_name in original dataset
    # by averaging pred with the main_var
    df[adjusted_var_name].loc[
        np.logical_and(df.index >= start_date, df.index <= end_date)
    ] = pred.reshape(1, -1)[0]

    return df


def adjust_var_and_place_in_data(period, data, var_to_adjust_name, main_var_name, adjusted_var_name):
    """This function adjusts a variable within a time period
    with respect to a main variable and updates the
    adjusted_var_name variable in the dataset

    Params:
        period: tuple with start and end dates of time period
        data: original dataframe
        var_to_adjust_name: name of the variable to adjust
        main_var_name: name of the main variable
        adjusted_var_name : name of the resulting variable

    """

    df = data.copy()
    # define start and end date of the period
    start_date = period[0]
    end_date = period[1]

    # subset the meaningful variables within period
    period_df = subset_period(df, start_date, end_date)

    var_to_adjust = period_df[var_to_adjust_name].values.reshape(-1, 1)
    main_var = period_df[main_var_name].values.reshape(-1, 1)

    # Fit Linear Regression with:
    # X=var_to_adjust, Y=main_var
    reg = LinearRegression().fit(var_to_adjust, main_var)

    # Calculate pred = reg.coef_*X + reg.intercept_
    pred = reg.predict(var_to_adjust)

    # Update the period adjusted_var_name in original dataset
    # by averaging pred with the main_var
    df[adjusted_var_name].loc[
        np.logical_and(df.index >= start_date, df.index <= end_date)
    ] = (pred.reshape(1, -1)[0] + period_df[main_var_name].values) / 2

    return df


def insert_data_to_tracker_mean_steps(period, data, main_var_name, adjusted_var_name):
    """This function insert the values of a variable within a time
    period in the "tracker_mean_steps" variable in the dataset

    Params:
        period: tuple with start and end dates of time period
        data: original dataframe
        main_var_name: name of the variable to insert
        adjusted_var_name : name of the adjusted variable

    """

    df = data.copy()
    # define start and end date of the period
    start_date = period[0]
    end_date = period[1]

    # subset the meaningful variables within period
    period_df = subset_period(df, start_date, end_date)

    # Update the period adjusted_var_name in original dataset
    # with the main_var values
    df[adjusted_var_name].loc[
        np.logical_and(df.index >= start_date, df.index <= end_date)
    ] = period_df[main_var_name].values

    return df

def transformPain(pain):
  for i in range(0, len(pain)):
    painIntensity = pain[i]
    if np.isnan(painIntensity):
      pain[i] = painIntensity
    else:
      if painIntensity < 2:
        pain[i] = 0
      if painIntensity < 2.5:
        pain[i] = 1
      elif painIntensity < 3:
        pain[i] = 2
      elif painIntensity < 3.3:
        pain[i] = 4
      elif painIntensity == 3.3:
        pain[i] = 7
      elif painIntensity <= 3.5:
        pain[i] = 8
      else:
        pain[i] = 10
  return pain


def rollingMinMaxScaler(data, columnName, window):
  
  dataForCol = data[columnName]
  data[columnName + "_2"] = data[columnName]
  
  for ind in range(0, len(dataForCol)):
    
    ind_start = ind - window/2
    ind_end   = ind + window/2
    if ind_start < 0:
      ind_start = 0
    if ind_end >= len(dataForCol):
      ind_end = len(dataForCol) - 1
    
    minn = min(dataForCol[int(ind_start):int(ind_end)])
    maxx = max(dataForCol[int(ind_start):int(ind_end)])
    
    val  = dataForCol[ind]
    
    if np.isnan((val - minn) / (maxx - minn)) or np.isinf((val - minn) / (maxx - minn)):
      if ind:
        data[columnName + "_2"][ind] = data[columnName + "_2"][ind - 1]
      else:
        data[columnName + "_2"][ind] = 0
    else:
      data[columnName + "_2"][ind] = (val - minn) / (maxx - minn)
    
    
  return data[columnName + "_2"]


def rollingMinMaxScalerMeanShift(data, columnName, window, windowMean):
  
  dataForCol = data[columnName]
  data[columnName + "_2"] = data[columnName]
  
  for ind in range(0, len(dataForCol)):
    
    ind_start = ind - window + windowMean
    ind_end   = ind + windowMean
    if ind_start < 0:
      ind_start = 0
    if ind_end >= len(dataForCol):
      ind_end = len(dataForCol) - 1
    
    minn = min(dataForCol[int(ind_start):int(ind_end)])
    maxx = max(dataForCol[int(ind_start):int(ind_end)])
    
    val  = dataForCol[ind]
    
    if np.isnan((val - minn) / (maxx - minn)) or np.isinf((val - minn) / (maxx - minn)):
      if ind:
        data[columnName + "_2"][ind] = data[columnName + "_2"][ind - 1]
      else:
        data[columnName + "_2"][ind] = 0
    else:
      data[columnName + "_2"][ind] = (val - minn) / (maxx - minn)
        
  return data[columnName + "_2"]
