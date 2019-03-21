import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def selectTime(data, deb, end):
  data2 = data.loc[data.index > deb]
  data2 = data2.loc[data2.index < end]
  return data2

def selectColumns(data, columnList):
  data2 = data[columnList]
  return data2

def addRollingMeanColumns(data, columnList, window):
  scaler = MinMaxScaler()
  data[columnList] = scaler.fit_transform(data[columnList])
  for var in columnList:
    data[var+'RollingMean'] = data[var].rolling(window).mean()
  return data
