import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler


def selectTime(data, deb, end):
    data2 = data.loc[data.index >= deb]
    data2 = data2.loc[data2.index <= end]
    return data2


def selectColumns(data, columnList):
    data2 = data[columnList]
    return data2


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


def adjustVarAndPlaceInData(
    period, data, varToAdjustName, mainVarName, startDate, endDate
):
    varToAdjust = period[varToAdjustName].values.reshape(-1, 1)
    mainVar = period[mainVarName].values.reshape(-1, 1)
    reg = LinearRegression().fit(varToAdjust, mainVar)
    pred = reg.predict(varToAdjust)
    data["trackerMeanSteps"].loc[
        np.logical_and(data.index >= startDate, data.index <= endDate)
    ] = (pred.reshape(1, -1)[0] + period[mainVarName].values) / 2
    return data


def addDataToTrackerMeanSteps(period, data, mainVarName, startDate, endDate):
    data["trackerMeanSteps"].loc[
        np.logical_and(data.index >= startDate, data.index <= endDate)
    ] = period[mainVarName].values
    return data
