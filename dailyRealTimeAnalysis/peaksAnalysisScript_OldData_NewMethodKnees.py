from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import os
from applyPeaksAnalysisOnRegion import applyPeaksAnalysisOnRegion
import sys
sys.path.insert(1, '../src/MyAIGuide/dataFromGarmin')
from garminDataGatheredFromWebExport import garminDataGatheredFromWebExport, garminActivityDataGatheredFromWebExport
sys.path.insert(1, '../src/MyAIGuide/utilities')
from dataFrameUtilities import rollingMinMaxScalerMeanShift
sys.path.insert(1, '../february2023ResearchGatePaperScripts')
import peakAnalysis_compute
import peakAnalysis_plot
import peakAnalysis_stats


# Most important variables

reloadMostRecentlyGeneratedData = True
reloadDataFrom14_11_2023 = False
reloadOldData = False

analysisOnBothDateRangeExtremities = True

rollingMeanWindow = 15
rollingMinMax = 270
rollingMedianWindow = 15

removeDataAfterApril2022    = False
removeDataBeforeJanuary2016 = False

plotTimeInitialTimeSeries = True
plotFinalHistograms = True

allCyclingDaysHomegenous = False
coeffKnee = {'tracker_mean_distance': 1, 'tracker_mean_denivelation': 1, 'cycling': 2, 'swimmingKm': 0.5, 'timeDrivingCar': 0.2, 'manicTimeDelta_corrected': 1}



### Reloading data

inputt = open("../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb")


data = pickle.load(inputt)
inputt.close()
data.loc[data.index < '2016-02-15', 'wholeArm'] = 2.8
print(data.columns)

if removeDataAfterApril2022:
  data = data[data.index <= '2022-03-28']

if removeDataBeforeJanuary2016:
  data = data[data.index >= '2016-01-01']


# Knee load analysis

if allCyclingDaysHomegenous:
  data['cycling'] = data['cycling'].apply(lambda x: 1 if x != 0 else 0)
  
data['tracker_mean_denivelation'] = data['tracker_mean_denivelation'].fillna(0)

predictors = ['tracker_mean_distance', 'tracker_mean_denivelation', 'cycling', 'swimmingKm', 'timeDrivingCar', 'manicTimeDelta_corrected']

region = 'knee'

[maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, minpeaks, maxpeaks, maxstrainScores2, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee, maxpeaksstrain] = applyPeaksAnalysisOnRegion(data, coeffKnee, plotTimeInitialTimeSeries, rollingMeanWindow, rollingMinMax, rollingMedianWindow, analysisOnBothDateRangeExtremities, predictors, region)


### Histograms and statistics

createFigs = False

statisticScores = peakAnalysis_stats.computeStatisticalSignificanceTests(maxstrainScoresKnee, totDaysDescendingPainKnee, totDaysAscendingPainKnee)
if plotFinalHistograms:
  fig, axes = plt.subplots(nrows=1, ncols=1)
  peakAnalysis_plot.plotMaxStrainLocationInMinMaxCycle(maxstrainScoresKnee, totDaysDescendingPainKnee, totDaysAscendingPainKnee, createFigs)


