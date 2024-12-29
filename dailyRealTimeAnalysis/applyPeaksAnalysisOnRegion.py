from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(1, '../src/MyAIGuide/dataFromGarmin')
from garminDataGatheredFromWebExport import garminDataGatheredFromWebExport, garminActivityDataGatheredFromWebExport
sys.path.insert(1, '../src/MyAIGuide/utilities')
from dataFrameUtilities import rollingMinMaxScalerMeanShift
sys.path.insert(1, '../february2023ResearchGatePaperScripts')
import peakAnalysis_compute
import peakAnalysis_plot
import peakAnalysis_stats

def applyPeaksAnalysisOnRegion(data, coeffKnee, plotTimeInitialTimeSeries, rollingMeanWindow, rollingMinMax, rollingMedianWindow, analysisOnBothDateRangeExtremities, predictors, region):

  figWidth  = 20
  figHeight = 5.1
  hspace   = 0.4

  minProminenceForPeakDetect = 0.08 #0.075
  windowForLocalPeakMinMaxFind = 5
  plotZoomedGraph = False
  minMaxTimeToleranceMinus = 0
  minMaxTimeTolerancePlus = 0
  plotGraphStrainDuringDescendingPain = False
  zoomedGraphNbDaysMarginLeft = 14
  zoomedGraphNbDaysMarginRight = 14
  createFigs = False
  plotGraphs = False
  
  scaler = MinMaxScaler()

  data[predictors] = scaler.fit_transform(data[predictors])
  
  data[region + 'Load'] = 0
  for predictor in predictors:
    data[region + 'Load'] = data[region + 'Load'] + coeffKnee[predictor] * data[predictor]

  for variable in [region + 'Load', region + 'Pain']:
    if analysisOnBothDateRangeExtremities:
      data[variable + "_RollingMean"] = data[variable].rolling(rollingMeanWindow, min_periods=1).mean().shift(int(-rollingMeanWindow/2)).fillna(0)
    else:
      data[variable + "_RollingMean"] = data[variable].rolling(rollingMeanWindow).mean().shift(int(-rollingMeanWindow/2))
    rollingMinMaxScalerMeanShift(data, variable + "_RollingMean", rollingMinMax, rollingMeanWindow)
    data.rename(columns={variable + '_RollingMean_2': variable + '_RollingMean_MinMax'}, inplace=True)
    if analysisOnBothDateRangeExtremities:
      data[variable + "_RollingMean_MinMax_Median"] = data[variable + "_RollingMean_MinMax"].rolling(rollingMedianWindow, min_periods=1).median().shift(int(-rollingMedianWindow/2)).fillna(0)
    else:
      data[variable + "_RollingMean_MinMax_Median"] = data[variable + "_RollingMean_MinMax"].rolling(rollingMedianWindow).median().shift(int(-rollingMedianWindow/2))

  data[[region + 'Load_RollingMean_MinMax_Median', region + 'Pain_RollingMean_MinMax_Median']] = scaler.fit_transform(data[[region + 'Load_RollingMean_MinMax_Median', region + 'Pain_RollingMean_MinMax_Median']])

  data[[region + 'Load', region + 'Pain']] = scaler.fit_transform(data[[region + 'Load', region + 'Pain']])

  data['regionSpecificstrain_RollingMean_MinMaxScaler'] = data[region + 'Load_RollingMean_MinMax_Median']
  data[region + '_RollingMean_MinMaxScaler'] = data[region + 'Pain_RollingMean_MinMax_Median']

  [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, minpeaks, maxpeaks, maxstrainScores2, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee, maxpeaksstrain] = peakAnalysis_compute.addMinAndMax(data, region, plotGraphs, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, [], plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight, createFigs)

  if plotTimeInitialTimeSeries:

    plot1Vars = [region + 'Load', region + 'Pain']
    colors1   = ['blue', 'red']
    labels1   = [region + 'Load', region + 'Pain']

    plot2Vars = [region + 'Load_RollingMean_MinMax_Median', region + 'Pain_RollingMean_MinMax_Median']
    colors2   = ['blue', 'red']
    labels2   = [region + 'Load', region + 'Pain']

    fig, axes = plt.subplots(figsize=(figWidth, figHeight), nrows=2, ncols=1)
    fig.subplots_adjust(left=0.05, bottom=0.1, right=0.98, top=0.95, wspace=None, hspace=hspace)

    for col, color, label in zip(plot1Vars, colors1, labels1):
      data[col].plot(ax=axes[0], color=color, label=label)
    axes[0].legend(loc='upper left')

    for col, color, label in zip(plot2Vars, colors2, labels2):
      data[col].plot(ax=axes[1], color=color, label=label)
    axes[1].legend(loc='upper left')
    
    
    nonNanLocations = np.argwhere(~np.isnan(maxstrainScoresKnee))
    nonNanLocations = nonNanLocations.flatten()

    maxpeaksstrain  = maxpeaksstrain[nonNanLocations]
    maxstrainScoresKnee = maxstrainScoresKnee[nonNanLocations]
    
    if not(createFigs):
      plt.xticks([data.index[ind] for ind in maxpeaksstrain], [int(val*100)/100 for val in maxstrainScoresKnee], rotation='vertical')
    
    plt.show()
  
  
  return [maxstrainScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, minpeaks, maxpeaks, maxstrainScores2, strainMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee, maxpeaksstrain]