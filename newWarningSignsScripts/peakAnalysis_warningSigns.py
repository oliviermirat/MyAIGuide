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

def peakAnalysis_warningSigns(hspace, data, dataWithRollingMedian, dataWithRollingMedianNoDropVars, strain_and_pain, strain_and_pain_rollingMean, strain_and_pain_RollingMean_MinMaxScaler, rollingMedianWindow, window2):
  
  # Past pain time ranges comparisons
  timeRange = window2
  halfTimeRange = int(timeRange / 2)
  print("Time window of pain vs recent pain calculation:", halfTimeRange, "days")
  # Warning Thresholds
  strainValueSmallThresh = 0.4
  strainValueBigThresh   = 0.6
  strainDiffThresh       = 0.02
  # Various options
  calculateStrainDiffWithMinMaxScaler = True
  plotLinearRegression   = False
  plot4binsTotHistograms = False
  warningOnlyForHighStrainValue = False
  calculateWarningSignOnlyWithDifferential = True
  removeLastNbDays = 20 #20
  
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
      count = 10
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
  warningDatesBig       = []
  warningValuesBigPlot2 = []
  warningValuesBigPlot3 = []
  warningValuesBigpainNowVsRecentPast = []
  for i in range(len(dataRolling_Mean_Median) - 1):
    if dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "distanceFromWarning"] == 1 and i > window2:
      if np.sum([dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[j], "strainFinalTooHigh"] == 0.600001 for j in range(i, i+7)]) > 0:
        warningDatesBig.append(dataRolling_Mean_Median.index[i].to_pydatetime().date())
        warningValuesBigPlot2.append(0.6)
        warningValuesBigpainNowVsRecentPast.append(dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "painNowVsRecentPast"])
        warningValuesBigPlot3.append(dataRolling_Mean_MinMax_Median.iloc[i][strain_and_pain_RollingMean_MinMaxScaler[1]])
      else:
        warningDatesSmall.append(dataRolling_Mean_Median.index[i].to_pydatetime().date())
        warningValuesSmallPlot2.append(0.6)
        warningValuesSmallpainNowVsRecentPast.append(dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[i], "painNowVsRecentPast"])
        warningValuesSmallPlot3.append(dataRolling_Mean_MinMax_Median.iloc[i][strain_and_pain_RollingMean_MinMaxScaler[1]])
  
  ### First Figure:
  fig, axes = plt.subplots(nrows=6, ncols=1)
  fig.subplots_adjust(left=0.02, bottom=0.05, right=0.90, top=0.97, wspace=None, hspace=hspace)
  # First plot
  data[strain_and_pain_rollingMean].plot(ax=axes[0], linestyle='-', marker='o', markersize=0.5, color=['k','r'])
  # Second plot
  data[strain_and_pain_RollingMean_MinMaxScaler].plot(ax=axes[1], linestyle='-', marker='o', markersize=0.5, color=['k','r'])
  # Third plot
  dataRolling_Mean_MinMax_Median[strain_and_pain_RollingMean_MinMaxScaler[0]].plot(ax=axes[2])
  dataRolling_Mean_Median[["strainDiff"]].plot(ax=axes[2])
  # Fourth plot
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainValueTooHigh"] == 0, "strainValueTooHigh"] = float('NaN')
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainDiffTooHigh"]  == 0, "strainDiffTooHigh"]  = float('NaN')
  dataRolling_Mean_Median.loc[dataRolling_Mean_Median["strainFinalTooHigh"] == 0, "strainFinalTooHigh"] = float('NaN')
  if calculateWarningSignOnlyWithDifferential:
    dataRolling_Mean_Median[["strainDiffTooHigh", "strainFinalTooHigh"]].plot(ax=axes[3], color=['b', 'r'])
  else:
    dataRolling_Mean_Median[["strainValueTooHigh", "strainDiffTooHigh", "strainFinalTooHigh"]].plot(ax=axes[3], color=['g', 'b', 'r'])
    axes[3].plot(warningDatesSmall, warningValuesSmallPlot2, marker='x', linestyle='', color='orange', markeredgewidth=2)
  axes[3].plot(warningDatesBig, warningValuesBigPlot2, marker='x', linestyle='', color='red', markeredgewidth=2)
  # Fifth plot
  dataWithRollingMedianNoDropVars[[strain_and_pain_RollingMean_MinMaxScaler[1]]].plot(ax=axes[4], color=['b'])
  axes[4].plot(warningDatesSmall, warningValuesSmallPlot3, marker='x', linestyle='', color='orange', markeredgewidth=2)
  axes[4].plot(warningDatesBig, warningValuesBigPlot3, marker='x', linestyle='', color='red', markeredgewidth=2)
  # Sixth plot
  dataRolling_Mean_Median[["painNowVsRecentPast"]].plot(ax=axes[5], color=['b'])
  axes[5].plot(warningDatesSmall, warningValuesSmallpainNowVsRecentPast, marker='x', linestyle='', color='orange', markeredgewidth=2)
  axes[5].plot(warningDatesBig, warningValuesBigpainNowVsRecentPast, marker='x', linestyle='', color='red', markeredgewidth=2)
  axes[5].plot(dataRolling_Mean_Median.index, [0 for i in range(len(dataRolling_Mean_Median.index))], color='k')
  # Pritting out all plots
  peakAnalysis_plot.plottingOptions(axes, 0, 'Rolling Mean of Strain (linear combination of stressors) and Pain', ['Strain', 'Pain'], 'center left', 8, createFigs)
  peakAnalysis_plot.plottingOptions(axes, 1, 'Rolling Mean + MinMaxScaler of: Strain and Pain', ['Strain', 'Pain'], 'center left', 8, createFigs)
  peakAnalysis_plot.plottingOptions(axes, 2, "Strain (Rolling: Mean + MinMaxScaler + Median) and its differential", ['Strain Value', 'Strain Differential'], 'center left', 8, 0, True)
  if calculateWarningSignOnlyWithDifferential:
    peakAnalysis_plot.plottingOptions(axes, 3, "Warnings based on previously filtered strain", ['Strain Diff Warn', 'Warning Line', 'Warning Point'], 'center left', 8, 0, True)  
  else:
    peakAnalysis_plot.plottingOptions(axes, 3, "Warnings based on previously filtered strain", ['Strain Value Warn', 'Strain Diff Warn', 'Warning Line', 'Low Warning', 'High Warning'], 'center left', 8, 0, True)
  peakAnalysis_plot.plottingOptions(axes, 4, "Warnings superimposed on 'Pain' (with rolling: Mean + MinMaxScaler + Median)", ['Pain', 'Low Warning', 'High Warning'], 'center left', 8, 0, True)
  peakAnalysis_plot.plottingOptions(axes, 5, "Warnings superimposed on 'Pain on current day - Mean pain during the last 45 days' (from pain variable above)", ['Pain', 'Low Warning', 'High Warning'], 'center left', 8, 0, True, False)
  axes[5].get_xaxis().set_visible(True)
  if createFigs:
    plt.savefig('./folderToSaveFigsIn/fig_1.png')
  else:
    plt.show()
  
  ### Getting the dataframes: 'distFromWarningList', 'painNowVsRecentPastList' and 'warningSuiteList' within the relevant time periods
  distFromWarningList = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "distanceFromWarning"]
  painNowVsRecentPastList     = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "painNowVsRecentPast"]
  strainList = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "regionSpecificstrain_RollingMean"]
  warningSuiteList    = dataRolling_Mean_Median.loc[dataRolling_Mean_Median.index[window2]:dataRolling_Mean_Median.index[len(dataWithRollingMedianNoDropVars) - 1], "curWarningSuiteNumber"]
  print("Number of sequences in between the subsequent warnings:", nb)
  
  if removeLastNbDays > 0:
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
  plt.xlabel("Number of days since last warning occured")
  plt.ylabel("Pain on current day - Mean pain during the last 45 days")
  plt.show()
  
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
  plt.show()
  
  ### Fourth Figure: Histograms plots of painNowVsRecentPastList as a function of distFromWarningList
  fig, axs = plt.subplots(1, 2, figsize=(12, 5))
  nb_x_bins = 10
  nb_y_bins = 10
  x_bins = np.linspace(0, max(abs(distFromWarningList)), nb_x_bins + 1)
  y_bins = np.linspace(-max(abs(painNowVsRecentPastList)),     max(abs(painNowVsRecentPastList)),     nb_y_bins + 1)
  histdata, xedges, yedges = np.histogram2d(distFromWarningList, painNowVsRecentPastList, bins=(x_bins, y_bins))
  histdata = histdata.T
  axs[1].hist2d(distFromWarningList, painNowVsRecentPastList, bins=(x_bins, y_bins))
  axs[1].set_xlabel("Number of days since last warning occured")
  axs[1].set_ylabel("Pain on current day - Mean pain during the last 45 days")
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
  else:
    for i in range(0, len(histdata)):
      histdata[:, i] = histdata[:, i] / np.sum(histdata[:, i])
    axs[1].imshow(histdata, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', aspect='auto')
    axs[1].set_xlabel("Number of days since last warning occured")
    axs[1].set_ylabel("Pain on current day - Mean pain during the last 45 days")
    axs[1].set_title("Histogram normalized for each column")
    fig.colorbar(axs[1].imshow(histdata, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', aspect='auto'), ax=axs[1])
    plt.tight_layout()
  plt.show()

  ### Fifth Figure: Histograms plots of painNowVsRecentPastList as a function of distFromWarningList
  if plot4binsTotHistograms:
    nb_x_bins = 2
    nb_y_bins = 2
    x_bins = np.linspace(0, max(abs(distFromWarningList)), nb_x_bins + 1)
    y_bins = np.linspace(-max(abs(painNowVsRecentPastList)),     max(abs(painNowVsRecentPastList)),     nb_y_bins + 1)
    histdata, xedges, yedges = np.histogram2d(distFromWarningList, painNowVsRecentPastList, bins=(x_bins, y_bins))
    histdata = histdata.T
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].hist2d(distFromWarningList, painNowVsRecentPastList, bins=(x_bins, y_bins))
    axs[0].set_xlabel("Number of days since last warning occured")
    axs[0].set_ylabel("Pain on current day - Mean pain during the last 45 days")
    axs[0].set_title("Histogram")
    fig.colorbar(axs[0].collections[0], ax=axs[0])
    for i in range(0, len(histdata)):
      histdata[:, i] = histdata[:, i] / np.sum(histdata[:, i])
    axs[1].imshow(histdata, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', aspect='auto')
    axs[1].set_xlabel("Number of days since last warning occured")
    axs[1].set_ylabel("Pain on current day - Mean pain during the last 45 days")
    axs[1].set_title("Histogram normalized for each column")
    fig.colorbar(axs[1].imshow(histdata, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', aspect='auto'), ax=axs[1])
    plt.tight_layout()
    plt.show()
  
  if False:
    print(histdata)
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    diffHist = histdata[1, :] - histdata[0, :]
    totElem  = histdata[1, :] + histdata[0, :]
    axs[0].plot(diffHist)
    axs[0].plot(totElem)
    plt.show()
  
  