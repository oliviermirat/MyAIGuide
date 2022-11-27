import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import os

zoomedGraphHeight = 2.5 #3.2

def addMinAndMax(data, regionName, plotFig, minProminenceForPeakDetect, windowForLocalPeakMinMaxFind, dataOriginal = [], plotZoomedGraph = False, minMaxTimeTolerancePlus=0, minMaxTimeToleranceMinus=0, plotGraphStrainDuringDescendingPain=False, zoomedGraphNbDaysMarginLeft=14, zoomedGraphNbDaysMarginRight=14, createFigs=False):
  
  if createFigs:
    plotZoomedGraph = True
    plotGraphStrainDuringDescendingPain = True
    if os.path.isdir('./folderToSaveFigsIn/' + regionName):
      shutil.rmtree('./folderToSaveFigsIn/' + regionName)
    os.mkdir('./folderToSaveFigsIn/' + regionName)
  
  scoreBasedOnAmplitude = False
  debugMode = False
  debugModeGeneral = False
  
  if plotZoomedGraph:
    zoomedGraphToSave = []
  
  # Finding local min and max of pain and removing subsquent min/max not separated by respectively max/min
  pain = np.array(data[regionName+'_RollingMean_MinMaxScaler'].tolist())
  maxpeaks, properties = find_peaks(pain, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  minpeaks, properties = find_peaks(-pain, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  if True:
    if plotFig:
      print("Before double max peaks removal: len(maxpeaks):", len(maxpeaks))
      print("Before double min peaks removal: len(minpeaks):", len(minpeaks))
    # Removing "double max peaks"
    lastSeenWasMaxPeak = False
    for i in range(0, len(data)):
      if i in maxpeaks:
        if lastSeenWasMaxPeak:
          maxpeaks = maxpeaks[maxpeaks != i]
        lastSeenWasMaxPeak = True
      if i in minpeaks:
        lastSeenWasMaxPeak = False
    # Removing "double min peaks"
    lastSeenWasMinPeak = False
    for i in range(0, len(data)):
      if i in minpeaks:
        if lastSeenWasMinPeak:
          minpeaks = minpeaks[minpeaks != i]
        lastSeenWasMinPeak = True
      if i in maxpeaks:
        lastSeenWasMinPeak = False
    if plotFig:
      print("After double max peaks removal: len(maxpeaks):", len(maxpeaks))
      print("After double min peaks removal: len(minpeaks):", len(minpeaks))
  
  # Storing in memory the sequence of mins and max
  painMinMaxSequence = []
  isMinOrMaxSequence = []
  for i in range(0, len(data)):
      if i in maxpeaks:
        painMinMaxSequence.append(i)
        isMinOrMaxSequence.append(True)
      if i in minpeaks:
        painMinMaxSequence.append(i)
        isMinOrMaxSequence.append(False)
  
  # Adding two columns in dataframe equal to pain values at min/max frame and to nan elsewhere
  data['max'] = float('nan')
  data['max'][maxpeaks] = data[regionName+'_RollingMean_MinMaxScaler'][maxpeaks].tolist()
  data['min'] = float('nan')
  data['min'][minpeaks] = data[regionName+'_RollingMean_MinMaxScaler'][minpeaks].tolist()
  
  # Finding strain min/max
  strain = np.array(data['regionSpecificstrain_RollingMean_MinMaxScaler'].tolist())
  maxpeaksstrain, properties = find_peaks(strain, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  minpeaksstrain, properties = find_peaks(-strain, prominence=minProminenceForPeakDetect, width=windowForLocalPeakMinMaxFind)
  data['maxstrain'] = float('nan')
  
  # Calculates for each strain peak the relative location in the min/max pain cycle
  negativeValue = 0
  positiveValue = 0
  # -1 : maxstrain slightly above maxPain
  # 0  : maxstrain at minPain
  # 1  : maxstrain slightly below maxPain
  maxstrainScores  = np.array([float('nan') for i in range(0, len(maxpeaksstrain))])
  maxstrainScores2 = np.array([float('nan') for i in range(0, len(maxpeaksstrain))])
  if plotGraphStrainDuringDescendingPain:
    fig, ax1 = plt.subplots(4, 4, figsize=(15, 10))
    # fig.subplots_adjust(left=0.14, bottom=0.14, right=0.98, top=0.98)
    maxDerivateWithStrainInDescendingPain = []
  figInd = 0
  for ind, maxstrain in enumerate(maxpeaksstrain):
    indSequencePain = 0
    while indSequencePain + 1 < len(painMinMaxSequence) and not(painMinMaxSequence[indSequencePain] <= maxstrain and maxstrain <= painMinMaxSequence[indSequencePain + 1]):
      indSequencePain = indSequencePain + 1
    if indSequencePain + 1 < len(painMinMaxSequence) and painMinMaxSequence[indSequencePain] <= maxstrain and maxstrain <= painMinMaxSequence[indSequencePain + 1]:
      closestMaxPain = painMinMaxSequence[indSequencePain]   if isMinOrMaxSequence[indSequencePain] else painMinMaxSequence[indSequencePain+1]
      closestMinPain = painMinMaxSequence[indSequencePain+1] if isMinOrMaxSequence[indSequencePain] else painMinMaxSequence[indSequencePain]
      keepMaxPeakstrain = False
      # if False and (maxstrain >= closestMaxPain): # maxstrain >= closestMaxPain
      if maxstrain >= closestMaxPain: # maxstrain >= closestMaxPain
        minPainCandidates = np.array([minPain for minPain in minpeaks if minPain >= closestMaxPain and maxstrain <= minPain])
        if len(minPainCandidates):
          keepMaxPeakstrain = True
          closestMinPain = minPainCandidates[0]
          # closestMaxPain <= maxstrain <= closestMinPain
          maxstrainScores[ind] = (maxstrain - closestMinPain) / (closestMinPain - closestMaxPain) # Negative value
          maxstrainScores2[ind] = pain[maxstrain+1] - pain[maxstrain] if maxstrain + 1 < len(pain) else 0
          if plotFig:
            print("strain peak relative location (Negative):", maxstrainScores[ind], "; Time:", data.index[maxstrain])
          negativeValue += 1
      else: # maxstrain < closestMaxPain
        minPainCandidates = np.array([minPain for minPain in minpeaks if minPain <= closestMaxPain and minPain <= maxstrain])
        # if len(minPainCandidates) and (pain[painMinMaxSequence[indSequencePain+1]] - pain[painMinMaxSequence[indSequencePain]]) > 0.3:
        if len(minPainCandidates):
          keepMaxPeakstrain = True
          closestMinPain = minPainCandidates[-1:][0]
          # closestMinPain <= maxstrain <= closestMaxPain
          maxstrainScores[ind] = (maxstrain - closestMinPain) / (closestMaxPain - closestMinPain) # Positive value
          maxstrainScores2[ind] = pain[maxstrain+1] - pain[maxstrain] if maxstrain + 1 < len(pain) else 0
          if plotFig:
            print("strain peak relative location (Positive):", maxstrainScores[ind], "; Time:", data.index[maxstrain])
          positiveValue += 1
      if keepMaxPeakstrain:
        if True:
          # if True:
            # minstrainCandidates = np.array([minstrainPeak for minstrainPeak in minpeaksstrain if minstrainPeak <= maxstrain])
            # minstrainPeak = minstrainCandidates[-1] if len(minstrainCandidates) else 0 # "else 0" needs to be improved
          data['maxstrain'][maxstrain - 1] = 0
          data['maxstrain'][maxstrain]     = data['regionSpecificstrain_RollingMean_MinMaxScaler'][maxstrain] # strain[maxstrain] - strain[minstrainPeak]
          data['maxstrain'][maxstrain + 1] = 0     
        else:
          data['maxstrain'][maxstrain - 1] = 0.5
          data['maxstrain'][maxstrain]     = 0.5 + maxstrainScores[ind]/2
          data['maxstrain'][maxstrain + 1] = 0.5
      
      
      if plotGraphStrainDuringDescendingPain and maxstrainScores[ind] >= -0.8 and maxstrainScores[ind] <= -0.2:
        scaler = MinMaxScaler()
        nbDaysMargin = 0
        dateMin = data.index[painMinMaxSequence[indSequencePain] - nbDaysMargin]
        dateMax = data.index[painMinMaxSequence[indSequencePain+1] + nbDaysMargin]
        dataWtFilt = data[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler', 'max',  'min', 'maxstrain']].copy()
        dataWtFilt = dataWtFilt[np.logical_and((dataWtFilt.index >= dateMin), (dataWtFilt.index <= dateMax))]
        dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']] = scaler.fit_transform(dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']])
        maxDerivateWithStrainInDescendingPain.append(np.max(np.diff(dataWtFilt[[regionName + '_RollingMean_MinMaxScaler']].to_numpy()[:, 0])))
        dataWtFilt['max'][[i for i, val in enumerate(dataWtFilt['max'].isna() == False) if val]] = dataWtFilt[regionName + '_RollingMean_MinMaxScaler'][[i for i, val in enumerate(dataWtFilt['max'].isna() == False) if val]]
        dataWtFilt['min'][[i for i, val in enumerate(dataWtFilt['min'].isna() == False) if val]] = dataWtFilt[regionName + '_RollingMean_MinMaxScaler'][[i for i, val in enumerate(dataWtFilt['min'].isna() == False) if val]]
        dataWtFilt['maxstrain'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] != 0)) if val]] = dataWtFilt['regionSpecificstrain_RollingMean_MinMaxScaler'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] != 0)) if val]]
        dataWtFilt['maxstrain'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] == 0)) if val]] = float('NaN')
        dataWtFilt = dataWtFilt.reset_index()
        dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].plot(ax=ax1[int(figInd/4), figInd % 4], color = ['blue', 'red'])
        dataWtFilt[['max', 'min', 'maxstrain']].plot(ax=ax1[int(figInd/4), figInd % 4], linestyle='', marker='o', color = ['black', 'black', 'green'], markersize = 10)
        if int(figInd/4) == 0 and figInd % 4 == 3 and not(createFigs):
          ax1[int(figInd/4), figInd % 4].legend(['strainFiltered', 'painFiltered', 'maxPainPeak', 'minPainPeak', 'maxStrainPeak', 'strain', 'pain'], loc="center left", bbox_to_anchor=(1, 0.5))
        else:
          ax1[int(figInd/4), figInd % 4].legend().remove()
        if not(createFigs):
          plt.title("Strain relative location: " + str(maxstrainScores[ind]))
        else:
          # ax1[int(figInd/4), figInd % 4].get_legend().remove()
          ax1[int(figInd/4), figInd % 4].xaxis.set_major_locator(MaxNLocator(4))
          ax1[int(figInd/4), figInd % 4].yaxis.set_major_locator(MaxNLocator(5))
        figInd += 1
      
      
      if plotZoomedGraph and (maxstrainScores[ind] >= 0 or maxstrainScores[ind] < -0.8):
        scaler = MinMaxScaler()
        dateMin = data.index[painMinMaxSequence[indSequencePain] - zoomedGraphNbDaysMarginLeft]
        dateMax = data.index[painMinMaxSequence[indSequencePain+1] + zoomedGraphNbDaysMarginRight]
        dataWtFilt = data[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler', 'max',  'min', 'maxstrain']].copy()
        dataNoFilt = dataOriginal[['regionSpecificstrain', regionName]].copy() #, 'regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].copy()
        dataWtFilt = dataWtFilt[np.logical_and((dataWtFilt.index >= dateMin), (dataWtFilt.index <= dateMax))]
        dataNoFilt = dataNoFilt[np.logical_and((dataNoFilt.index >= dateMin), (dataNoFilt.index <= dateMax))]
        dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']] = scaler.fit_transform(dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']])
        
        dataWtFilt['max'][[i for i, val in enumerate(dataWtFilt['max'].isna() == False) if val]] = dataWtFilt[regionName + '_RollingMean_MinMaxScaler'][[i for i, val in enumerate(dataWtFilt['max'].isna() == False) if val]]
        dataWtFilt['min'][[i for i, val in enumerate(dataWtFilt['min'].isna() == False) if val]] = dataWtFilt[regionName + '_RollingMean_MinMaxScaler'][[i for i, val in enumerate(dataWtFilt['min'].isna() == False) if val]]
        dataWtFilt['maxstrain'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] != 0)) if val]] = dataWtFilt['regionSpecificstrain_RollingMean_MinMaxScaler'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] != 0)) if val]]
        dataWtFilt['maxstrain'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] == 0)) if val]] = float('NaN')
        # dataNoFilt[['regionSpecificstrain', regionName, 'regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']] = scaler.fit_transform(dataNoFilt[['regionSpecificstrain', regionName, 'regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']])
        dataNoFilt[['regionSpecificstrain', regionName]] = scaler.fit_transform(dataNoFilt[['regionSpecificstrain', regionName]])
        
        dataNoFilt = dataNoFilt.reset_index()
        dataWtFilt = dataWtFilt.reset_index()
        
        # Saving individual graph
        fig2, ax2 = plt.subplots(1, 1, figsize=(7.5, zoomedGraphHeight))
        if False:
          dataNoFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].plot(ax=ax2, color = ['blue', 'red'])
        else:
          dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].plot(ax=ax2, color = ['blue', 'red'])
          dataWtFilt[['max', 'min', 'maxstrain']].plot(ax=ax2, linestyle='', marker='o', color = ['black', 'black', 'green'], markersize = 10)
        dataNoFilt[['regionSpecificstrain', regionName]].plot(ax=ax2, linestyle='', marker='o', color = ['blue', 'red']) #, markersize=1)
        if not(createFigs):
          ax2.legend(['strainFiltered', 'painFiltered', 'maxPainPeak', 'minPainPeak', 'maxStrainPeak', 'strain', 'pain'], loc="center left", bbox_to_anchor=(1, 0.5))
          plt.title("Strain relative location: " + str(maxstrainScores[ind]))
          plt.plot()
        else:
          ax2.get_legend().remove()
          ax2.xaxis.set_major_locator(MaxNLocator(4))
          ax2.yaxis.set_major_locator(MaxNLocator(5))
          fig2.subplots_adjust(left=0.15, bottom=0.20, right=0.98, top=0.98)
          # fig2.subplots_adjust(left=0.15, bottom=0.17, right=0.98, top=0.98)
          plt.xlabel('Time (in days)')
          plt.ylabel('Values normalized over interval')
          fig2.savefig('./folderToSaveFigsIn/' + regionName + '/' + str(ind) + '_' + str(data.index[maxstrain])[0:10] + '.svg')
        zoomedGraphToSave.append({'maxStrainScore': maxstrainScores[ind], 'data': pd.concat([dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler', 'max', 'min', 'maxstrain']], dataNoFilt[['regionSpecificstrain', regionName]]], axis=1)})
        plt.close(fig2)
  
  if plotZoomedGraph:
    if not(createFigs):
      with open('zoomedGraph.pkl', 'wb') as handle:
        pickle.dump(zoomedGraphToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
      with open('./folderToSaveFigsIn/' + regionName + '/zoomedGraph.pkl', 'wb') as handle:
        pickle.dump(zoomedGraphToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)      
  
  if plotGraphStrainDuringDescendingPain:
    if not(createFigs):
      plt.show()
    else:
      # plt.xlabel('Time (in days)')
      # plt.ylabel('Values normalized over interval')
      fig.savefig('./folderToSaveFigsIn/' + regionName + '_descendingPainWithStrainPresent.svg')
      plt.close()
    
    maxDerivateNoStrainInDescendingPain = []
    fig, ax1 = plt.subplots(4, 4, figsize=(15, 10))
    figInd = 0
    graphNum = 0
    for indSequencePain in range(0, len(painMinMaxSequence)):
      # Selecting only the descending pain periods
      if indSequencePain + 1 < len(painMinMaxSequence) and isMinOrMaxSequence[indSequencePain]:
        closestMaxPain = painMinMaxSequence[indSequencePain]
        closestMinPain = painMinMaxSequence[indSequencePain+1]
        indStrain = 0
        maxstrain = maxpeaksstrain[indStrain]
        isDescendingPainPeriodWithoutMaxStrain = True
        # Making sure the descending pain period doesn't contain a maxStrainPeak
        while indStrain < len(maxpeaksstrain):
          maxstrain = maxpeaksstrain[indStrain]
          if closestMaxPain <= maxstrain and maxstrain <= closestMinPain:
            isDescendingPainPeriodWithoutMaxStrain = False
          indStrain += 1
        if isDescendingPainPeriodWithoutMaxStrain:
          scaler = MinMaxScaler()
          nbDaysMargin = 0
          dateMin = data.index[painMinMaxSequence[indSequencePain] - nbDaysMargin]
          dateMax = data.index[painMinMaxSequence[indSequencePain+1] + nbDaysMargin]
          dataWtFilt = data[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler', 'max',  'min', 'maxstrain']].copy()
          dataWtFilt = dataWtFilt[np.logical_and((dataWtFilt.index >= dateMin), (dataWtFilt.index <= dateMax))]
          dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']] = scaler.fit_transform(dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']])
          maxDerivateNoStrainInDescendingPain.append(np.max(np.diff(dataWtFilt[[regionName + '_RollingMean_MinMaxScaler']].to_numpy()[:, 0])))
          dataWtFilt['max'][[i for i, val in enumerate(dataWtFilt['max'].isna() == False) if val]] = dataWtFilt[regionName + '_RollingMean_MinMaxScaler'][[i for i, val in enumerate(dataWtFilt['max'].isna() == False) if val]]
          dataWtFilt['min'][[i for i, val in enumerate(dataWtFilt['min'].isna() == False) if val]] = dataWtFilt[regionName + '_RollingMean_MinMaxScaler'][[i for i, val in enumerate(dataWtFilt['min'].isna() == False) if val]]
          dataWtFilt['maxstrain'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] != 0)) if val]] = dataWtFilt['regionSpecificstrain_RollingMean_MinMaxScaler'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] != 0)) if val]]
          dataWtFilt['maxstrain'][[i for i, val in enumerate(np.logical_and(dataWtFilt['maxstrain'].isna() == False, dataWtFilt['maxstrain'] == 0)) if val]] = float('NaN')
          dataWtFilt = dataWtFilt.reset_index()
          dataWtFilt[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].plot(ax=ax1[int(figInd/4), figInd % 4], color = ['blue', 'red'])
          dataWtFilt[['max', 'min', 'maxstrain']].plot(ax=ax1[int(figInd/4), figInd % 4], linestyle='', marker='o', color = ['black', 'black', 'green'], markersize = 10)
          if int(figInd/4) == 0 and figInd % 4 == 3 and not(createFigs):
            ax1[int(figInd/4), figInd % 4].legend(['strainFiltered', 'painFiltered', 'maxPainPeak', 'minPainPeak', 'maxStrainPeak', 'strain', 'pain'], loc="center left", bbox_to_anchor=(1, 0.5))
          else:
            ax1[int(figInd/4), figInd % 4].legend().remove()
          if not(createFigs):
            plt.title("Strain relative location: " + str(maxstrainScores[ind]))
          else:
            # ax1.get_legend().remove()
            ax1[int(figInd/4), figInd % 4].xaxis.set_major_locator(MaxNLocator(4))
            ax1[int(figInd/4), figInd % 4].yaxis.set_major_locator(MaxNLocator(5))
          figInd += 1
          
          if figInd == 16:
            if not(createFigs):
              plt.show()
            else:
              fig.savefig('./folderToSaveFigsIn/' + regionName + 'descendingPainWithNoStrainPeak_' + str(graphNum) + '.svg')
              graphNum += 1
              plt.close()
            fig, ax1 = plt.subplots(4, 4, figsize=(15, 10))
            figInd = 0
  
  
  if debugModeGeneral: print("negativeValue:", negativeValue)
  if debugModeGeneral: print("positiveValue:", positiveValue)
  
  # Calculating total number of days where the pain is respectively ascending and descending
  minPeak = minpeaks[0] if len(minpeaks) else 0
  totDaysAscendingPain  = 0
  totDaysDescendingPain = 0
  toAddAscending  = []
  toAddDescending = []
  for maxPeak in maxpeaks:
    if minPeak < maxPeak:
      toAddAscending.append(maxPeak - minPeak)
      # totDaysAscendingPain += maxPeak - minPeak
      if debugMode: print("should be positive 1: ", maxPeak - minPeak)
    minPeakCandidates = np.array([minPain for minPain in minpeaks if minPain >= maxPeak])
    if len(minPeakCandidates):
      minPeak = minPeakCandidates[0]
      toAddDescending.append(minPeak - maxPeak)
      # totDaysDescendingPain += minPeak - maxPeak
      if debugMode: print("should be positive 2: ", minPeak - maxPeak)
    else:
      minPeak = -1
  totDaysAscendingPain = np.sum(np.array(toAddAscending[1:-1]))
  totDaysDescendingPain = np.sum(np.array(toAddDescending[1:-1]))
  if debugModeGeneral: print("totDaysAscendingPain:", totDaysAscendingPain)
  if debugModeGeneral: print("totDaysDescendingPain:", totDaysDescendingPain)
  
  # Plotting for each strain peak the relative location in the min/max pain cycle
  if plotFig:
    fig2, axes = plt.subplots(nrows=1, ncols=1)
    sns.stripplot(y="col1", data=pd.DataFrame(data={'col1': maxstrainScores}), size=4, color=".3", linewidth=0)
    plt.show()
    fig2, axes = plt.subplots(nrows=1, ncols=1)
    plt.hist(maxstrainScores)
    plt.show()
  
  # Relative locations of closest maxStrain for each maxPain
  if False:
    relativeLocation2 = []
    for maxPainPeak in maxpeaks:
      minPainCandidates  = np.array([minPainPeak for minPainPeak in minpeaks if minPainPeak <= maxPainPeak])
      minPainCandidates2 = np.array([minPainPeak for minPainPeak in minpeaks if minPainPeak >  maxPainPeak])
      if len(minPainCandidates) and len(minPainCandidates2):
        minPainPeak  = minPainCandidates[-1] if len(minPainCandidates)  else maxPainPeak
        minPainPeak2 = minPainCandidates2[0] if len(minPainCandidates2) else maxPainPeak
        correspondingstrainPeakCandidates = []
        for maxstrain in maxpeaksstrain:
          if maxstrain >= minPainPeak - minMaxTimeToleranceMinus and maxstrain <= minPainPeak2 + minMaxTimeTolerancePlus:
            if maxstrain < maxPainPeak:
              relativeLoc = (maxstrain - minPainPeak)  / (maxPainPeak - minPainPeak) 
            else:
              relativeLoc = (maxstrain - minPainPeak2) / (minPainPeak2 - maxPainPeak)
            correspondingstrainPeakCandidates.append(relativeLoc)
        if len(correspondingstrainPeakCandidates):
          maxstrainPeak = correspondingstrainPeakCandidates[np.argmax([abs(correspondingstrainPeakCandidates[idx]) for idx, maxstrain in enumerate(correspondingstrainPeakCandidates)])]
          print("maxstrainPeak:", maxstrainPeak)
          relativeLocation2.append(maxstrainPeak)
        else:
          print("One max pain peak without a maxstrain in the preceding ascending pain or subsequent descending pain period") 
          # relativeLocation2.append(-1.5)
    fig7, axes = plt.subplots(nrows=1, ncols=1)
    plt.hist(relativeLocation2, range=(-1, 1))
    plt.legend()
    plt.title("Relative locations of closest maxStrain for each maxPain:")
    plt.show()
    
  # Strain peaks amplitudes vs Pain peaks amplitudes: calculating values
  painMinMaxAmplitudes   = []
  strainMinMaxAmplitudes = []
  if True:
    analyzestrainResponseAfter = False
    for maxPainPeak in maxpeaks:
      minPainCandidates = np.array([minPainPeak for minPainPeak in minpeaks if minPainPeak <= maxPainPeak])
      if len(minPainCandidates):
        minPainPeak = minPainCandidates[-1]
        correspondingstrainPeakCandidates = [maxstrain for maxstrain in maxpeaksstrain if maxstrain >= minPainPeak - minMaxTimeToleranceMinus and maxstrain <= maxPainPeak + minMaxTimeTolerancePlus]
        if len(correspondingstrainPeakCandidates):
          maxstrainPeak = correspondingstrainPeakCandidates[np.argmax([strain[maxstrain] for maxstrain in correspondingstrainPeakCandidates])]
          minstrainCandidates = np.array([minstrainPeak for minstrainPeak in minpeaksstrain if minstrainPeak <= maxstrainPeak]) if not(analyzestrainResponseAfter) else np.array([minstrainPeak for minstrainPeak in minpeaksstrain if minstrainPeak >= maxstrainPeak])
          if len(minstrainCandidates):
            minstrainPeak = minstrainCandidates[-1] if not(analyzestrainResponseAfter) else minstrainCandidates[0]
            painMinMaxAmplitudes.append(pain[maxPainPeak] - pain[minPainPeak])
            strainMinMaxAmplitudes.append(strain[maxstrainPeak] - strain[minstrainPeak])
            if plotFig:
              print("date: ", data.index[maxPainPeak], "; pain: ", pain[maxPainPeak] - pain[minPainPeak], "; strain: ", strain[maxstrainPeak] - strain[minstrainPeak])
        else: # THIS ELSE MIGHT NEED TO BE REMOVED
          painMinMaxAmplitudes.append(pain[maxPainPeak] - pain[minPainPeak])
          strainMinMaxAmplitudes.append(0)
          if plotFig:
            print("date: ", data.index[maxPainPeak], "; pain: ", pain[maxPainPeak] - pain[minPainPeak], "; strain: ", 0)
  
  if plotFig:
    print("max:", [data.index[peak] for peak in maxpeaks])
    print("min:", [data.index[peak] for peak in minpeaks])
    
  if plotGraphStrainDuringDescendingPain:
    if not(createFigs):
      with open('descendingPeriodsMaxDerivative.pkl', 'wb') as handle:
        pickle.dump([maxDerivateNoStrainInDescendingPain, maxDerivateWithStrainInDescendingPain], handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
      with open('./folderToSaveFigsIn/' + regionName + '/descendingPeriodsMaxDerivative.pkl', 'wb') as handle:
        pickle.dump([maxDerivateNoStrainInDescendingPain, maxDerivateWithStrainInDescendingPain], handle, protocol=pickle.HIGHEST_PROTOCOL)      
  
  return [maxstrainScores, totDaysAscendingPain, totDaysDescendingPain, minpeaks, maxpeaks, maxstrainScores2, strainMinMaxAmplitudes, painMinMaxAmplitudes, maxpeaksstrain]
