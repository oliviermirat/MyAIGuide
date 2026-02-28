import peakAnalysis_compute
import peakAnalysis_plot
from dataFrameUtilities import rollingMinMaxScalerMeanShift
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math

createFigs = False
figWidth   = 9 #7.2
figHeight  = 0.9
figHeight2 = 5.5
hspace   = 0.4
if createFigs:
  plt.rcParams.update({'font.size': 12})

def peakAnalysis_warningSigns(hspace, data, dataWithRollingMedian, dataWithRollingMedianNoDropVars, strain_and_pain, strain_and_pain_rollingMean, strain_and_pain_RollingMean_MinMaxScaler, rollingMedianWindow, window2, list_of_stressors):
  
  # Past pain time ranges comparisons
  timeRange = window2
  halfTimeRange = int(timeRange / 2)
  print("Time window of pain vs recent pain calculation:", halfTimeRange, "days")
  # Warning Thresholds
  strainValueSmallThresh = 0.4
  strainValueBigThresh   = 0.6
  strainDiffThresh       = 0.02
  nbDaysWithoutStrainDiffTooHighForWarningDetectionPossible = 10
  # Various options
  calculateStrainDiffWithMinMaxScaler = True
  plotLinearRegression   = False
  warningOnlyForHighStrainValue = False
  calculateWarningSignOnlyWithDifferential = True
  alsoPlotTracesInSeparateFigures = False
  plotNbDaysWithoutWarningVsMinPainInLast20days = False
  
  removeLastNbDays  = 20
  removeLastFewDays = True
  
  if warningOnlyForHighStrainValue:
    strainFinalThresholdForWarning = 0.600001
  else:
    strainFinalThresholdForWarning = 0.6
  
  ### Warnings signs calculations
  # Calculation strain differential over time
  dataRolling_Mean_Median = data[strain_and_pain_rollingMean].copy()
  dataRolling_Mean_MinMax_Median = data[strain_and_pain_RollingMean_MinMaxScaler].copy()
  dataRolling_Mean_Median = dataRolling_Mean_Median.rolling(rollingMedianWindow).median().shift(int(-rollingMedianWindow/2))
  dataRolling_Mean_MinMax_Median = dataRolling_Mean_MinMax_Median.rolling(rollingMedianWindow).median().shift(int(-rollingMedianWindow/2))
  if calculateStrainDiffWithMinMaxScaler:
    dataRolling_Mean_Median["strainDiff"] = dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]].copy()
    dataRolling_Mean_Median["strainDiff"] = dataRolling_Mean_Median["strainDiff"].diff()
  else:
    dataRolling_Mean_Median["strainDiff"] = dataRolling_Mean_Median[strain_and_pain_rollingMean[0]].copy()
    dataRolling_Mean_Median["strainDiff"] = dataRolling_Mean_Median["strainDiff"].diff()
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[0]:dataRolling_Mean_Median.index[window2], "strainDiff"] = float('NaN')
  # Calculating strainDiffTooHigh variable
  dataRolling_Mean_Median["strainDiffTooHigh"] = 0
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainDiff"] >= strainDiffThresh, "strainDiffTooHigh"] = 0.48
  count = 0
  for i in range(window2, len(dataRolling_Mean_Median) - 1):
    if dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainDiffTooHigh"] == 0.48:
      count = nbDaysWithoutStrainDiffTooHighForWarningDetectionPossible
    else:
      if count:
        dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainDiffTooHigh"] = 0.4
        count -= 1
  # Calculating strainValueTooHigh variable
  dataRolling_Mean_Median["strainValueTooHigh"] = 0
  dataRolling_Mean_Median.loc[dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]] >= strainValueSmallThresh, "strainValueTooHigh"] = 0.25
  dataRolling_Mean_Median.loc[dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]] >= strainValueBigThresh, "strainValueTooHigh"] = 0.52
  # Calculating strainFinalTooHigh variable
  dataRolling_Mean_Median["strainFinalTooHigh"] = 0
  for i in range(window2, len(dataRolling_Mean_Median) - 1):
    if calculateWarningSignOnlyWithDifferential:
      if (dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainDiffTooHigh"] >= 0.4):
        dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainFinalTooHigh"] = 0.600001
    else:
      if (dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainDiffTooHigh"] >= 0.4) and (dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainValueTooHigh"] == 0.52):
        dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainFinalTooHigh"] = 0.600001 #0.5
      if (dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainDiffTooHigh"] >= 0.4) and (dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainValueTooHigh"] == 0.25):
        dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainFinalTooHigh"] = 0.6 #0.25
  
  # Calculating for each day:
  # - the 'warnings': the days for which the strainFinalTooHigh becomes different than zeros
  # - the 'distanceFromWarning': the number of days since a last warning occurred
  # - the 'painNowVsRecentPast': the difference between the pain on that day and the mean pain in the next halfTimeRange days
  # - the 'warningSuiteNumber': the ID of the current sequence in between the subsequent warnings
  dataRolling_Mean_Median["distanceFromWarning"] = 0
  dataRolling_Mean_Median["warningSuiteNumber"] = 0
  dataRolling_Mean_Median["painNowVsRecentPast"] = float('NaN')
  currentlyInAlert = 0
  nb = 0
  curWarningSuiteNumber = 1
  curWarningSuiteNumber_To_indEndSequence   = {}
  curWarningSuiteNumber_To_indStartSequence = {}
  curWarningSuiteNumber_To_indStartSequence[curWarningSuiteNumber] = window2
  for i in range(window2, len(dataWithRollingMedianNoDropVars)):
    # distance from warning
    dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "distanceFromWarning"] = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i-1], "distanceFromWarning"] + 1
    if dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "strainFinalTooHigh"] >= strainFinalThresholdForWarning:        
      if currentlyInAlert == 0:
        dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "distanceFromWarning"] = 1
        nb += 1
        curWarningSuiteNumber_To_indEndSequence[curWarningSuiteNumber]   = i
        curWarningSuiteNumber += 1
        curWarningSuiteNumber_To_indStartSequence[curWarningSuiteNumber] = i
      currentlyInAlert = 1
    else:
      currentlyInAlert = 0
    # curWarningSuiteNumber
    dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "curWarningSuiteNumber"] = curWarningSuiteNumber
    # painNowVsRecentPast
    dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "painNowVsRecentPast"] = dataWithRollingMedianNoDropVars.loc[dataWithRollingMedianNoDropVars.index[i], strain_and_pain_RollingMean_MinMaxScaler[1]] - dataWithRollingMedianNoDropVars.loc[dataWithRollingMedianNoDropVars.index[i-halfTimeRange]:dataWithRollingMedianNoDropVars.index[i], strain_and_pain_RollingMean_MinMaxScaler[1]].mean()
  curWarningSuiteNumber_To_indEndSequence[curWarningSuiteNumber] = len(dataWithRollingMedianNoDropVars)
  # Warning dates calculation
  warningDatesSmall       = []
  warningValuesSmallPlot2 = []
  warningValuesSmallPlot3 = []
  warningValuesSmallpainNowVsRecentPast = []
  warningValuesSmallStrain = []
  warningDatesBig       = []
  warningValuesBigPlot2 = []
  warningValuesBigPlot3 = []
  warningValuesBigpainNowVsRecentPast = []
  warningValuesBigStrain = []
  for i in range(len(dataRolling_Mean_Median) - 1):
    if dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "distanceFromWarning"] == 1 and i > window2:
      if np.sum([dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[j], "strainFinalTooHigh"] == 0.600001 for j in range(i, i+7)]) > 0:
        warningDatesBig.append(dataRolling_Mean_Median.index[i].to_pydatetime().date())
        warningValuesBigPlot2.append(0.6)
        warningValuesBigpainNowVsRecentPast.append(dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "painNowVsRecentPast"])
        warningValuesBigPlot3.append(dataRolling_Mean_MinMax_Median.iloc[i][strain_and_pain_RollingMean_MinMaxScaler[1]])
        warningValuesBigStrain.append(dataRolling_Mean_MinMax_Median.iloc[i][strain_and_pain_RollingMean_MinMaxScaler[0]])
      else:
        warningDatesSmall.append(dataRolling_Mean_Median.index[i].to_pydatetime().date())
        warningValuesSmallPlot2.append(0.6)
        warningValuesSmallpainNowVsRecentPast.append(dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "painNowVsRecentPast"])
        warningValuesSmallPlot3.append(dataRolling_Mean_MinMax_Median.iloc[i][strain_and_pain_RollingMean_MinMaxScaler[1]])
        warningValuesSmallStrain.append(dataRolling_Mean_MinMax_Median.iloc[i][strain_and_pain_RollingMean_MinMaxScaler[0]])
  
  if createFigs:
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
    data[list_of_stressors].plot(ax=axes, linestyle='', marker='o', markersize=0.5)
    axes.set_ylim([0, 1])
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_0.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
    data[strain_and_pain].plot(ax=axes, linestyle='', marker='o', markersize=0.5, color=['k','r'])
    axes.set_ylim([0, 1])
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_0b.svg')
    plt.close()
  
  ### First Figure:
  if createFigs:
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    fig, axes = plt.subplots(nrows=6, ncols=1)
    fig.subplots_adjust(left=0.02, bottom=0.05, right=0.90, top=0.97, wspace=None, hspace=hspace)
  # First plot
  if createFigs:
    data[strain_and_pain_rollingMean].plot(ax=axes, linestyle='-', marker='o', markersize=0.5, color=['k','r'])
    axes.set_ylim([0, 1])
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_1.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    data[strain_and_pain_rollingMean].plot(ax=axes[0], linestyle='-', marker='o', markersize=0.5, color=['k','r'])
  # Second plot
  if createFigs:
    data[strain_and_pain_RollingMean_MinMaxScaler].plot(ax=axes, linestyle='-', marker='o', markersize=0.5, color=['k','r'])
    axes.set_ylim([0, 1])
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_2.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    data[strain_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[1], linestyle='-', marker='o', markersize=0.5, color=['k','r'])
  # Third plot
  if createFigs:
    dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]].plot(ax=axes, color=["k"])
    dataRolling_Mean_Median[["strainDiff"]].plot(ax=axes, color=["gray"])
    axes.set_ylim([0, 1])
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_3.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]].plot(ax=axes[2], color=["k"])
    dataRolling_Mean_Median[["strainDiff"]].plot(ax=axes[2], color=["gray"])
  # Fourth plot
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainValueTooHigh"] == 0, "strainValueTooHigh"] = float('NaN')
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainDiffTooHigh"]  == 0, "strainDiffTooHigh"]  = float('NaN')
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainFinalTooHigh"] == 0, "strainFinalTooHigh"] = float('NaN')
  if createFigs:
    if calculateWarningSignOnlyWithDifferential:
      dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]].plot(ax=axes, color=['k'])
      dataRolling_Mean_Median[["strainDiff"]].plot(ax=axes, color=['gray'])
    else:
      dataRolling_Mean_Median[["strainValueTooHigh", "strainDiffTooHigh", "strainFinalTooHigh"]].plot(ax=axes, color=['g', 'b', 'r'])
      axes.plot(warningDatesSmall, warningValuesSmallPlot2, marker='x', linestyle='', color='orange', markeredgewidth=2)
    axes.plot(warningDatesBig, warningValuesBigStrain, marker='x', linestyle='', color='blue', markeredgewidth=2)
    axes.set_ylim([0, 1])
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_4.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    if calculateWarningSignOnlyWithDifferential:
      dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]].plot(ax=axes[3], color=['k'])
      dataRolling_Mean_Median[["strainDiff"]].plot(ax=axes[3], color=['gray'])
    else:
      dataRolling_Mean_Median[["strainValueTooHigh", "strainDiffTooHigh", "strainFinalTooHigh"]].plot(ax=axes[3], color=['g', 'b', 'r'])
      axes[3].plot(warningDatesSmall, warningValuesSmallStrain, marker='x', linestyle='', color='orange', markeredgewidth=2)
    axes[3].plot(warningDatesBig, warningValuesBigStrain, marker='x', linestyle='', color='blue', markeredgewidth=2)
  # Fifth plot
  if createFigs:
    dataWithRollingMedianNoDropVars[[strain_and_pain_RollingMean_MinMaxScaler[1]]].plot(ax=axes, color=['r'])
    axes.plot(warningDatesSmall, warningValuesSmallPlot3, marker='x', linestyle='', color='orange', markeredgewidth=2)
    axes.plot(warningDatesBig, warningValuesBigPlot3, marker='x', linestyle='', color='b', markeredgewidth=2)
    axes.get_legend().remove()
    axes.set_ylim([0, 1])
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_5.svg')
    plt.close()
    fig, axes = plt.subplots(figsize=(figWidth, figHeight), dpi=300, nrows=1, ncols=1)
    fig.subplots_adjust(left=0.04, bottom=0.25, right=0.98, top=0.95, wspace=None, hspace=hspace)
  else:
    dataWithRollingMedianNoDropVars[[strain_and_pain_RollingMean_MinMaxScaler[1]]].plot(ax=axes[4], color=['r'])
    axes[4].plot(warningDatesSmall, warningValuesSmallPlot3, marker='x', linestyle='', color='orange', markeredgewidth=2)
    axes[4].plot(warningDatesBig, warningValuesBigPlot3, marker='x', linestyle='', color='b', markeredgewidth=2)
  # Sixth plot
  if createFigs:
    dataRolling_Mean_Median[["painNowVsRecentPast"]].plot(ax=axes, color=['r'])
    axes.plot(warningDatesSmall, warningValuesSmallpainNowVsRecentPast, marker='x', linestyle='', color='orange', markeredgewidth=2)
    axes.plot(warningDatesBig, warningValuesBigpainNowVsRecentPast, marker='x', linestyle='', color='b', markeredgewidth=2)
    axes.plot(dataRolling_Mean_Median.index, [0 for i in range(len(dataRolling_Mean_Median.index))], color='k')
    axes.get_legend().remove()
    plt.savefig('./folderToSaveFigsIn/succussiveFilters_6.svg')
    plt.close()
  else:
    dataRolling_Mean_Median[["painNowVsRecentPast"]].plot(ax=axes[5], color=['r'])
    axes[5].plot(warningDatesSmall, warningValuesSmallpainNowVsRecentPast, marker='x', linestyle='', color='orange', markeredgewidth=2)
    axes[5].plot(warningDatesBig, warningValuesBigpainNowVsRecentPast, marker='x', linestyle='', color='b', markeredgewidth=2)
    axes[5].plot(dataRolling_Mean_Median.index, [0 for i in range(len(dataRolling_Mean_Median.index))], color='k')
  # Pritting out all plots
  if not(createFigs):
    peakAnalysis_plot.plottingOptions(axes, 0, 'Rolling Mean of Strain (linear combination of stressors) and Pain', ['Strain', 'Pain'], 'center left', 8, createFigs)
    peakAnalysis_plot.plottingOptions(axes, 1, 'Rolling Mean + MinMaxScaler of: Strain and Pain', ['Strain', 'Pain'], 'center left', 8, createFigs)
    peakAnalysis_plot.plottingOptions(axes, 2, "Strain (Rolling: Mean + MinMaxScaler + Median) and its differential", ['Strain Value', 'Strain Differential'], 'center left', 8, 0, True)
    if calculateWarningSignOnlyWithDifferential:
      peakAnalysis_plot.plottingOptions(axes, 3, "Warnings based on previously filtered strain", ['Strain Diff Warn', 'Warning Line', 'Warning Point'], 'center left', 8, 0, True)  
    else:
      peakAnalysis_plot.plottingOptions(axes, 3, "Warnings based on previously filtered strain", ['Strain Value Warn', 'Strain Diff Warn', 'Warning Line', 'Low Warning', 'High Warning'], 'center left', 8, 0, True)
    peakAnalysis_plot.plottingOptions(axes, 4, "Warnings superimposed on 'Pain' (with rolling: Mean + MinMaxScaler + Median)", ['Pain', 'Low Warning', 'High Warning'], 'center left', 8, 0, True)
    peakAnalysis_plot.plottingOptions(axes, 5, "Warnings superimposed on 'Pain on current day - Mean pain during the last " + str(halfTimeRange) + " days' (from pain variable above)", ['Pain', 'Low Warning', 'High Warning'], 'center left', 8, 0, True, False)
    axes[5].get_xaxis().set_visible(True)
    plt.show()
  
  ### Getting the dataframes: 'distFromWarningList', 'painNowVsRecentPastList' and 'warningSuiteList' within the relevant time periods
  distFromWarningList = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "distanceFromWarning"]
  painNowVsRecentPastList     = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "painNowVsRecentPast"]
  strainList = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "regionSpecificstrain_RollingMean"]
  warningSuiteList    = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "curWarningSuiteNumber"]
  print("Number of sequences in between the subsequent warnings:", nb)
  
  if removeLastNbDays > 0 and removeLastFewDays:
    startRemoving = 0
    distFromWarningListNew = distFromWarningList.copy()
    for i in range(1, len(distFromWarningList)):
      j = len(distFromWarningList) - 1 - i
      if distFromWarningList[j] + 1 != distFromWarningList[j + 1]:
        startRemoving = removeLastNbDays
      if startRemoving > 0:
        distFromWarningListNew[j] = -10
      startRemoving -= 1
    indToKeep = (distFromWarningListNew != -10)
    distFromWarningList     = distFromWarningList[indToKeep]
    painNowVsRecentPastList = painNowVsRecentPastList[indToKeep]
    strainList              = strainList[indToKeep]
    warningSuiteList        = warningSuiteList[indToKeep]
  
  ### Second Figure: Plot each sequences of painNowVsRecentPast in between the subsequent warnings
  if True: # if True plot for each time interval; if False plot everything combined
    distFromWarningList2 = []
    painNowVsRecentPastList2     = []
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      painNowVsRecentPastListI     = painNowVsRecentPastList[warningSuiteI]
      distFromWarningListI = distFromWarningList[warningSuiteI]
      plt.plot(distFromWarningListI, painNowVsRecentPastListI)
  else:
    plt.plot(distFromWarningList, painNowVsRecentPastList, '.')
  plt.plot([i for i in range(0, np.max(distFromWarningList), 10)], [0 for i in range(0, np.max(distFromWarningList), 10)], linewidth=1, color='k')
  if plotLinearRegression:
    reg = LinearRegression().fit(np.array([distFromWarningList]).reshape(-1, 1), np.array([painNowVsRecentPastList]).reshape(-1, 1))
    pred = reg.predict(np.array([i for i in range(0, np.max(distFromWarningList), 10)]).reshape(-1, 1))
    plt.plot([i for i in range(0, np.max(distFromWarningList), 10)], pred, linewidth=2, color='k')
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/painNowVsRecentPastInBetweenWarnings.svg')
    plt.close()  
  else:
    plt.xlabel("Number of days since last warning occured")
    plt.ylabel("Pain on current day - Mean pain during the last" + str(halfTimeRange) + "days")
    plt.show()
  
  if plotNbDaysWithoutWarningVsMinPainInLast20days:
    nbDaysWithoutWarning   = []
    painNowVsRecentPastEnd = []
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      if np.sum(warningSuiteI):
        painNowVsRecentPastListI = painNowVsRecentPastList[warningSuiteI]
        nbDays      = np.sum(warningSuiteI)
        # lastDayPain = painNowVsRecentPastListI[len(painNowVsRecentPastListI) - 1]
        lastDayPain = painNowVsRecentPastListI[len(painNowVsRecentPastListI)-removeLastNbDays:len(painNowVsRecentPastListI) - 1].min()
        if nbDays != float('nan') and lastDayPain != float('nan'):
          nbDaysWithoutWarning.append(nbDays)
          painNowVsRecentPastEnd.append(lastDayPain)
    plt.plot(nbDaysWithoutWarning, painNowVsRecentPastEnd, '.')
    if createFigs:
      plt.savefig('./folderToSaveFigsIn/plotNbDaysWithoutWarningVsMinPainInLast20days.svg')
      plt.close()
    else:
      plt.show()

  if alsoPlotTracesInSeparateFigures:
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      if np.sum(warningSuiteI) > 60 - removeLastNbDays:
        painNowVsRecentPastListI   = painNowVsRecentPastList[warningSuiteI]
        print("beginning of long trace:", painNowVsRecentPastListI.index[0], "; lenght of trace:", np.sum(warningSuiteI))
        distFromWarningListI = distFromWarningList[warningSuiteI]
        plt.plot(distFromWarningListI, painNowVsRecentPastListI)
    plt.xlim(0, 130)
    plt.ylim(-0.55, 0.55)
    plt.show()
    count = 0
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      if np.sum(warningSuiteI) <= 60 - removeLastNbDays:
        painNowVsRecentPastListI   = painNowVsRecentPastList[warningSuiteI]
        distFromWarningListI = distFromWarningList[warningSuiteI]
        plt.plot(distFromWarningListI, painNowVsRecentPastListI)
      if count == 10:
        plt.xlim(0, 130)
        plt.ylim(-0.55, 0.55)
        plt.show()
        count = 0
      count += 1
  
  ## Third Figure: Plot each sequences of strain in between the subsequent warnings
  nb_x_bins = 10
  nb_y_bins = 10
  for i in range(1, curWarningSuiteNumber+1):
    warningSuiteI = (warningSuiteList == i)
    strainListI   = strainList[warningSuiteI]
    distFromWarningListI = distFromWarningList[warningSuiteI]
    plt.plot(distFromWarningListI, strainListI)
  x_bins = np.linspace(0, max(abs(distFromWarningList)), nb_x_bins + 1)
  y_bins = np.linspace(-max(abs(distFromWarningList)),   max(abs(distFromWarningList)), nb_y_bins + 1)
  histdata, xedges, yedges = np.histogram2d(distFromWarningList, strainList, bins=(x_bins, y_bins))
  histdata = histdata.T
  x_intervals_median = []
  x_intervals_25   = []
  x_intervals_75   = []
  x_intervals_std = []
  for i in range(len(xedges) - 1):
    x_interval = [xedges[i], xedges[i + 1]]
    mask = (distFromWarningList >= x_interval[0]) & (distFromWarningList < x_interval[1])
    valuesInMask = np.array(strainList)[mask]
    valuesInMask = valuesInMask[~np.isnan(valuesInMask)]
    per50 = np.percentile(valuesInMask, 50)
    per75 = np.percentile(valuesInMask, 75)
    per25 = np.percentile(valuesInMask, 25)
    std = np.std(valuesInMask)
    x_intervals_median.append(per50)
    x_intervals_25.append(per25)
    x_intervals_75.append(per75)
    x_intervals_std.append(std)
    x_intervals_centers = 0.5 * (xedges[:-1] + xedges[1:])
  plt.errorbar(x_intervals_centers, x_intervals_median, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  plt.errorbar(x_intervals_centers, x_intervals_25, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  plt.errorbar(x_intervals_centers, x_intervals_75, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/strainInBetweenWarnings.svg')
    plt.close()
  else:
    plt.show()
  
  if alsoPlotTracesInSeparateFigures:
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      if np.sum(warningSuiteI) > 60 - removeLastNbDays:
        strainListI   = strainList[warningSuiteI]
        distFromWarningListI = distFromWarningList[warningSuiteI]
        plt.plot(distFromWarningListI, strainListI)
    plt.xlim(0, 130)
    plt.ylim(0, 1)
    plt.show()
    count = 0
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      if np.sum(warningSuiteI) <= 60 - removeLastNbDays:
        strainListI   = strainList[warningSuiteI]
        distFromWarningListI = distFromWarningList[warningSuiteI]
        plt.plot(distFromWarningListI, strainListI)
      if count == 10:
        plt.xlim(0, 130)
        plt.ylim(0, 1)
        plt.show()
        count = 0
      count += 1
      
  
  ### Fourth Figure: Histograms plots of painNowVsRecentPastList as a function of distFromWarningList
  fig, axs = plt.subplots(1, 2, figsize=(12, 5))
  nb_x_bins = 10
  nb_y_bins = 10
  x_bins = np.linspace(0, max(abs(distFromWarningList)), nb_x_bins + 1)
  y_bins = np.linspace(-max(abs(painNowVsRecentPastList)),     max(abs(painNowVsRecentPastList)),     nb_y_bins + 1)
  histdata, xedges, yedges = np.histogram2d(distFromWarningList, painNowVsRecentPastList, bins=(x_bins, y_bins))
  histdata = histdata.T
  if False:
    axs[1].hist2d(distFromWarningList, painNowVsRecentPastList, bins=(x_bins, y_bins))
    axs[1].set_xlabel("Number of days since last warning occured")
    axs[1].set_ylabel("Pain on current day - Mean pain during the last " + str(halfTimeRange) + " days")
    axs[1].set_title("Histogram")
    fig.colorbar(axs[1].collections[0], ax=axs[1])
  if True:
    x_intervals_median = []
    x_intervals_25   = []
    x_intervals_75   = []
    x_intervals_std = []
    for i in range(len(xedges) - 1):
      x_interval = [xedges[i], xedges[i + 1]]
      mask = (distFromWarningList >= x_interval[0]) & (distFromWarningList < x_interval[1])
      valuesInMask = np.array(painNowVsRecentPastList)[mask]
      valuesInMask = valuesInMask[~np.isnan(valuesInMask)]
      per50 = np.percentile(valuesInMask, 50)
      per75 = np.percentile(valuesInMask, 75)
      per25 = np.percentile(valuesInMask, 25)
      std = np.std(valuesInMask)
      x_intervals_median.append(per50)
      x_intervals_25.append(per25)
      x_intervals_75.append(per75)
      x_intervals_std.append(std)
      x_intervals_centers = 0.5 * (xedges[:-1] + xedges[1:])
    for i in range(1, curWarningSuiteNumber+1):
      warningSuiteI = (warningSuiteList == i)
      painNowVsRecentPastListI     = painNowVsRecentPastList[warningSuiteI]
      distFromWarningListI = distFromWarningList[warningSuiteI]
      axs[0].plot(distFromWarningListI, painNowVsRecentPastListI)
    axs[0].plot([i for i in range(0, np.max(distFromWarningList), 10)], [0 for i in range(0, np.max(distFromWarningList), 10)], linewidth=1, color='k')
    axs[0].errorbar(x_intervals_centers, x_intervals_median, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
    axs[0].errorbar(x_intervals_centers, x_intervals_25, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
    axs[0].errorbar(x_intervals_centers, x_intervals_75, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
    axs[0].set_title('Median + 25% and 75% Percentile')
    axs[0].set_xlabel('Number of days since last warning occured')
    axs[0].set_ylim([-max(abs(painNowVsRecentPastList)), max(abs(painNowVsRecentPastList))])
  else:
    for i in range(0, len(histdata)):
      histdata[:, i] = histdata[:, i] / np.sum(histdata[:, i])
    axs[1].imshow(histdata, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', aspect='auto')
    axs[1].set_xlabel("Number of days since last warning occured")
    axs[1].set_ylabel("Pain on current day - Mean pain during the last " + str(halfTimeRange) + " days")
    axs[1].set_title("Histogram normalized for each column")
    fig.colorbar(axs[1].imshow(histdata, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', aspect='auto'), ax=axs[1])
    plt.tight_layout()
  
  limit  = max(abs(painNowVsRecentPastList))
  yPlus  = np.array([limit for i in range(len(xedges))])
  yMinus = np.array([-limit for i in range(len(xedges))])
  axs[1].fill_between(xedges, yPlus,  where=(yPlus >= 0), color='red', alpha=0.5)
  axs[1].fill_between(xedges, yMinus, where=(yMinus < 0), color='green', alpha=0.5)
  
  axs[1].errorbar(x_intervals_centers, x_intervals_median, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  axs[1].errorbar(x_intervals_centers, x_intervals_25, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  axs[1].errorbar(x_intervals_centers, x_intervals_75, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  axs[1].set_ylim([-max(abs(painNowVsRecentPastList)), max(abs(painNowVsRecentPastList))])
  axs[1].set_title('Summary')
  axs[1].set_xlabel('Number of days since last warning occured')
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/quartilesTwoFigs.svg')
    plt.close()  
  else:
    plt.show()

  ### Fifth Figure
  fig, ax = plt.subplots()
  ax.fill_between(xedges, yPlus,  where=(yPlus >= 0), color='red', alpha=0.5)
  ax.fill_between(xedges, yMinus, where=(yMinus < 0), color='green', alpha=0.5)
  ax.errorbar(x_intervals_centers, x_intervals_median, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  ax.errorbar(x_intervals_centers, x_intervals_25, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  ax.errorbar(x_intervals_centers, x_intervals_75, fmt='o-', label='Mean with Std Dev', color='black', capsize=5, linewidth=3)
  ax.set_ylim([-max(abs(painNowVsRecentPastList)), max(abs(painNowVsRecentPastList))])
  ax.set_title('Summary')
  ax.set_xlabel('Number of days since last warning occured')
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/quartilesSummary.svg')
    plt.close()  
  else:
    plt.show()