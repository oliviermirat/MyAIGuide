import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler


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


def select_columns(data, column_list):
    """This function selects the columns of a dataframe
    according to a provided list of strings

    Params:
        data: original dataframe
        column_list: list of columns to select

    """

    return data[column_list].copy()


def addRollingMeanColumns(data, columnList, window):
    scaler = MinMaxScaler()
    data[columnList] = scaler.fit_transform(data[columnList])
    for var in columnList:
        data[var + "RollingMean"] = data[var].rolling(window).mean()
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


def adjust_var_and_place_in_data(
    period, data, var_to_adjust_name, main_var_name
):
    """This function adjusts a variable within a time period
    with respect to a main variable and updates the
    "tracker_mean_steps" variable in the dataset

    Params:
        period: tuple with start and end dates of time period
        data: original dataframe
        var_to_adjust_name: name of the variable to adjust
        main_var_name: name of the main variable

    """

    # define start and end date of the period
    start_date = period[0]
    end_date = period[1]

    # subset the meaningful variables within period
    period_df = subset_period(data, start_date, end_date)

    var_to_adjust = period_df[var_to_adjust_name].values.reshape(-1, 1)
    main_var = period_df[main_var_name].values.reshape(-1, 1)

    # Fit Linear Regression with:
    # X=var_to_adjust, Y=main_var
    reg = LinearRegression().fit(var_to_adjust, main_var)

    # Calculate pred = reg.coef_*X + reg.intercept_
    pred = reg.predict(var_to_adjust)

    # Update the period tracker_mean_steps in original dataset
    # by averaging pred with the main_var
    data["tracker_mean_steps"].loc[
        np.logical_and(data.index >= start_date, data.index <= end_date)
    ] = (pred.reshape(1, -1)[0] + period[main_var_name].values) / 2

    return data


def insert_data_to_tracker_mean_steps(period, data, main_var_name):
    """This function insert the values of a variable within a time
    period in the "tracker_mean_steps" variable in the dataset

    Params:
        period: tuple with start and end dates of time period
        data: original dataframe
        main_var_name: name of the variable to insert

    """

    # define start and end date of the period
    start_date = period[0]
    end_date = period[1]

    # subset the meaningful variables within period
    period_df = subset_period(data, start_date, end_date)

    # Update the period tracker_mean_steps in original dataset
    # with the main_var values
    data["tracker_mean_steps"].loc[
        np.logical_and(data.index >= start_date, data.index <= end_date)
    ] = period_df[main_var_name].values

    return data
