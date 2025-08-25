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

analysisOnBothDateRangeExtremities = True

rollingMeanWindow = 45
rollingMinMax = 270
rollingMedianWindow = 1 # 3

plotTimeInitialTimeSeries = True
plotFinalHistograms = True

coeffKnee = {'numberOfComputerClicksAndKeyStrokes': 3, 'climbingMaxEffortIntensity': 3, 'swimAndSurfStrokes': 3}

# coeffKnee = {'numberOfComputerClicksAndKeyStrokes': 1, 'climbingMaxEffortIntensity': 1, 'swimAndSurfStrokes': 1}



### Reloading data

inputt = open("dataMay2023andLater.pkl", "rb")

data = pickle.load(inputt)
inputt.close()

print(data.columns)


# Knee load analysis

# data['tracker_mean_denivelation'] = data['tracker_mean_denivelation'].fillna(0)

predictors = ['numberOfComputerClicksAndKeyStrokes', 'climbingMaxEffortIntensity', 'swimAndSurfStrokes']

region = 'arm'

[maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, minpeaks, maxpeaks, maxstrainScores2, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee, maxpeaksstrain] = applyPeaksAnalysisOnRegion(data, coeffKnee, plotTimeInitialTimeSeries, rollingMeanWindow, rollingMinMax, rollingMedianWindow, analysisOnBothDateRangeExtremities, predictors, region)


### Histograms and statistics

createFigs = False

statisticScores = peakAnalysis_stats.computeStatisticalSignificanceTests(maxstrainScoresKnee, totDaysDescendingPainKnee, totDaysAscendingPainKnee)
if plotFinalHistograms:
  fig, axes = plt.subplots(nrows=1, ncols=1)
  peakAnalysis_plot.plotMaxStrainLocationInMinMaxCycle(maxstrainScoresKnee, totDaysDescendingPainKnee, totDaysAscendingPainKnee, createFigs)


