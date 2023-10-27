import peakAnalysis_compute
import peakAnalysis_plot
import peakAnalysis_warningSigns as peakAnalysis_warningSigns
from dataFrameUtilities import rollingMinMaxScalerMeanShift
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

plotWithScaling = False
plotMedianGraph = True
createFigs = False # This also needs to be changed in peakAnalysis_launch
if createFigs:
  plt.rcParams.update({'font.size': 12})

def visualizeRollingMinMaxScalerofRollingMeanOfstrainAndPain(data, region, list_of_stressors, strainor_coef, window, window2, rollingMedianWindow, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, plotGraph, plotZoomedGraph=False, minMaxTimeTolerancePlus=0, minMaxTimeToleranceMinus=0, plotGraphStrainDuringDescendingPain=False, zoomedGraphNbDaysMarginLeft=14, zoomedGraphNbDaysMarginRight=14):
  
  if plotGraph and not(createFigs):
    if plotMedianGraph:
      fig, axes = plt.subplots(nrows=6, ncols=1)
    else:
      fig, axes = plt.subplots(nrows=5, ncols=1)
  
  figWidth = 7.2
  hspace   = 0.4
  
  if createFigs:
    fig, axes = plt.subplots(figsize=(figWidth, 1.7), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.35, right=0.98, top=0.75, wspace=None, hspace=hspace)
  else:
    if plotGraph:
      fig.subplots_adjust(left=0.02, bottom=0.05, right=0.90, top=0.97, wspace=None, hspace=hspace)
  
  scaler = MinMaxScaler()
  
  # Plotting potential stressors causing pain in region
  data[list_of_stressors] = scaler.fit_transform(data[list_of_stressors])
  if plotGraph:
    data[list_of_stressors].plot(ax=(axes[0] if not(createFigs) else axes), linestyle='', marker='o', markersize=0.5)
    peakAnalysis_plot.plottingOptions(axes, 0, 'Stressors causing ' + region, [], 'upper right' if plotWithScaling else 'center left', 3 if plotWithScaling else 8, createFigs, False if createFigs else True)
  
  if createFigs:
    axes.get_xaxis().set_visible(True)
    plt.savefig('./folderToSaveFigsIn/' + 'succussiveFilters_' + region + '_1.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, 5.25), dpi=300, nrows=4, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  
  # Plotting strain and pain
  strain_and_pain = ["regionSpecificstrain", region]
  data["regionSpecificstrain"] = np.zeros(len(data[list_of_stressors[0]]))
  for idx, strainor in enumerate(list_of_stressors):
    data["regionSpecificstrain"] = data["regionSpecificstrain"] + strainor_coef[idx] * data[strainor]
  data[strain_and_pain] = scaler.fit_transform(data[strain_and_pain])
  if plotGraph:
    data[strain_and_pain].plot(ax=axes[1 if not(createFigs) else 0], linestyle='', marker='o', markersize=0.5, color=['k','r'])
    peakAnalysis_plot.plottingOptions(axes, 1 if not(createFigs) else 0, 'Strain (linear combination of stressors) and pain', ['strain', 'pain'], 'center left', 8, createFigs)
  
  # Plotting Rolling Mean of strain and pain
  for var in strain_and_pain:
    data[var + "_RollingMean"] = data[var].rolling(window).mean().shift(int(-window/2))
  strain_and_pain_rollingMean = [name + "_RollingMean" for name in strain_and_pain]
  data[strain_and_pain_rollingMean] = scaler.fit_transform(data[strain_and_pain_rollingMean])
  if plotGraph:
    data[strain_and_pain_rollingMean].plot(ax=axes[2 if not(createFigs) else 1], color=['k','r'])
    peakAnalysis_plot.plottingOptions(axes, 2 if not(createFigs) else 1, 'Rolling mean applied', ['strain', 'pain'], 'center left', 8, createFigs)
  
  # Plotting Rolling MinMaxScaler of Rolling Mean of strain and pain
  strain_and_pain_RollingMean_MinMaxScaler = [name + "_MinMaxScaler" for name in strain_and_pain_rollingMean]
  if window2:
    for columnName in strain_and_pain_rollingMean:
      data[columnName + "_MinMaxScaler"] = rollingMinMaxScalerMeanShift(data, columnName, window2, window)
  else:
    for columnName in strain_and_pain_rollingMean:
      data[columnName + "_MinMaxScaler"] = data[columnName]
  if plotGraph:
    data[strain_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[3 if not(createFigs) else 2], color=['k','r'])
    peakAnalysis_plot.plottingOptions(axes, 3 if not(createFigs) else 2, 'Rolling MinMaxScaler applied', ['strain', 'pain'], 'center left', 8, createFigs)
  
  # Peaks analysis
  data2 = data[strain_and_pain_RollingMean_MinMaxScaler].copy()
  data2 = data2.rolling(rollingMedianWindow).median().shift(int(-rollingMedianWindow/2))
  if plotGraph and plotMedianGraph:
    data2[strain_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[4 if not(createFigs) else 3], color=['k','r'])
    data9 = data2[strain_and_pain_RollingMean_MinMaxScaler].copy()
    peakAnalysis_plot.plottingOptions(axes, 4 if not(createFigs) else 3, 'Rolling median applied', ['strain', 'pain'], 'center left', 8, createFigs)
    if createFigs:
      axes[3].get_xaxis().set_visible(True)
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/' + 'succussiveFilters_' + region + '_2.svg')
    plt.close()
  
  [maxstrainScores, totDaysAscendingPain, totDaysDescendingPain, minpeaks, maxpeaks, maxstrainScores2, strainMinMaxAmplitudes, painMinMaxAmplitudes, maxpeaksstrain] = peakAnalysis_compute.addMinAndMax(data2, region, False, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, data, plotZoomedGraph, minMaxTimeTolerancePlus, minMaxTimeToleranceMinus, plotGraphStrainDuringDescendingPain, zoomedGraphNbDaysMarginLeft, zoomedGraphNbDaysMarginRight, createFigs)
  
  if createFigs:
    fig, axes = plt.subplots(figsize=(figWidth, 1.7), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.35, right=0.98, top=0.75, wspace=None, hspace=hspace)
  
  data2 = peakAnalysis_plot.prepareForPlotting(data2, region, minpeaks, maxpeaks) # this is where some of the variables in data2 are dropped and thus why we need to copy data2 into data9 above
  if plotGraph:
    if plotMedianGraph:
      data2.plot(ax=axes[5 if not(createFigs) else 0] if not(createFigs) else axes)
      peakAnalysis_plot.plottingOptions(axes, 5 if not(createFigs) else 0, "Peaks Analysis", ['painAscending', 'painDescending', 'Peakstrain'], 'center left', 8, createFigs, False if createFigs else True)
      if not(createFigs):
        axes[5].get_xaxis().set_visible(True)
      else:
        axes.get_xaxis().set_visible(True)
    else:
      data2.plot(ax=axes[4 if not(createFigs) else 0])
      peakAnalysis_plot.plottingOptions(axes, 4 if not(createFigs) else 0, "Peaks Analysis", ['painAscending', 'painDescending', 'Peakstrain'], 'center left', 8, createFigs)
      if not(createFigs):
        axes[4].get_xaxis().set_visible(True)
      else:
        axes.get_xaxis().set_visible(True)
  
  nonNanLocations = np.argwhere(~np.isnan(maxstrainScores))
  nonNanLocations = nonNanLocations.flatten()

  maxpeaksstrain  = maxpeaksstrain[nonNanLocations]
  maxstrainScores = maxstrainScores[nonNanLocations]
  
  if not(createFigs):
    plt.xticks([data2.index[ind] for ind in maxpeaksstrain], [int(val*100)/100 for val in maxstrainScores], rotation='vertical')
  
  # Showing the final plot
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/' + 'succussiveFilters_' + region + '_3.svg')
    plt.close()
  else:
    if plotGraph:
      plt.show()

  if True:
    peakAnalysis_warningSigns.peakAnalysis_warningSigns(hspace, data, data2, data9, strain_and_pain, strain_and_pain_rollingMean, strain_and_pain_RollingMean_MinMaxScaler, rollingMedianWindow, window2)
      
  # Linear regression between strain and pain amplitudes
  if len(strainMinMaxAmplitudes):
    reg = LinearRegression().fit(np.array([strainMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1))
    if plotGraph:
      print("regression score:", reg.score(np.array([strainMinMaxAmplitudes]).reshape(-1, 1), np.array([painMinMaxAmplitudes]).reshape(-1, 1)))
    pred = reg.predict(np.array([i for i in range(0, 10)]).reshape(-1, 1))
    if plotGraph and not(createFigs):
      fig3, axes = plt.subplots(nrows=1, ncols=1)
      plt.plot(strainMinMaxAmplitudes, painMinMaxAmplitudes, '.')
      plt.plot([i for i in range(0, 10)], pred)
      plt.xlim([0, 1])
      plt.ylim([0, 1])
      plt.show()
  
  return [maxstrainScores, maxstrainScores2, totDaysAscendingPain, totDaysDescendingPain, data, data2, strainMinMaxAmplitudes, painMinMaxAmplitudes]