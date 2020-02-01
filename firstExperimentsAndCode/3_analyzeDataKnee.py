# This scripts assumes that the dataframe has been created and saved in data.txt

import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dataFrameUtilities import selectTime, selectColumns, addInsultIntensityColumns, getPainAboveThreshold, getInsultAboveThreshold
from sklearn.preprocessing import MinMaxScaler


# Getting data

input = open('data.txt', 'rb')
data = pickle.load(input)
input.close()

timeSelected = selectTime(data, '2016-09-01', '2019-10-20')


# Removing "steps" caused by scooter riding

timeSelected['steps'] = timeSelected['steps'] - 37 * timeSelected['scooterRiding']
timeSelected['steps'][timeSelected['steps'] < 0] = 0


# Getting knee pain information

kneePain = selectColumns(timeSelected, ['kneePain'])

thres = kneePain.copy()
thres[:] = 3.3


# Calculating knee stress over time

env = addInsultIntensityColumns(timeSelected, ['steps','kneePain'], 21, 30)
envRollingMean = selectColumns(env, ['stepsInsultIntensity'])
envMaxInsultDiff = selectColumns(env, ['stepsMaxInsultDiff'])

kneePainRollingMean = selectColumns(env, ['kneePainInsultIntensity'])
kneePainRollingMean = kneePainRollingMean.replace(0,0.4)
scaler = MinMaxScaler()
kneePainRollingMeanArray = scaler.fit_transform(kneePainRollingMean)
for i in range(0, len(kneePainRollingMean)):
  kneePainRollingMean['kneePainInsultIntensity'][i] = kneePainRollingMeanArray[i]
kneePainRollingMean = kneePainRollingMean.replace(0.0,0.4)

thres2 = kneePain.copy()
thres2[:] = 1.1
for i in range(0, 300):
  thres2['kneePain'][i] = 1.2
for i in range(810, len(thres2)):
  thres2['kneePain'][i] = 1.8

envBrut = selectColumns(env, ['steps'])

betterMaxInsult = envMaxInsultDiff.copy()
scaler = MinMaxScaler()
betterMaxInsultArray = scaler.fit_transform(betterMaxInsult)
for i in range(0, len(betterMaxInsult)):
  betterMaxInsult['stepsMaxInsultDiff'][i] = betterMaxInsultArray[i] + envBrut['steps'][i] + kneePainRollingMean['kneePainInsultIntensity'][i]

  
# Finding time points where knee pain and knee stress are above a certain threshold

painAboveThresh = getPainAboveThreshold(kneePain, 'kneePain', 3.3)
painAboveThresh = selectColumns(painAboveThresh, ['kneePainThreshed'])

stepsMaxInsultDiffThresh = getInsultAboveThreshold(betterMaxInsult, 'stepsMaxInsultDiff', thres2)
stepsMaxInsultDiffThresh = selectColumns(stepsMaxInsultDiffThresh, ['stepsMaxInsultDiffThreshed'])


# Plotting results

fig, axes = plt.subplots(nrows=3, ncols=1)

selectColumns(kneePain, ['kneePain']).rename(columns={"kneePain": "knee pain"}).plot(ax=axes[0])
thres.rename(columns={"kneePain": "pain threshold"}).plot(ax=axes[0])

selectColumns(betterMaxInsult, ['stepsMaxInsultDiff']).rename(columns={"stepsMaxInsultDiff": "knee stress"}).plot(ax=axes[1])
thres2.rename(columns={"kneePain": "knee stress threshold"}).plot(ax=axes[1])

painAboveThresh.rename(columns={"kneePainThreshed": "knee pain is above threshold"}).plot(ax=axes[2])
stepsMaxInsultDiffThresh = 0.95 * stepsMaxInsultDiffThresh
stepsMaxInsultDiffThresh.rename(columns={"stepsMaxInsultDiffThreshed": "knee stress is above threshold"}).plot(ax=axes[2])

leg = plt.legend(loc='best')
leg.draggable()
plt.show()
