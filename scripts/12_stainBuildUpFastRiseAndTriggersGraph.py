import matplotlib.pyplot as plt
import pickle as pkl
import numpy as np
import shutil
import os

zoomedPklFile = 'zoomedGraph_Participant1_Knee.pkl'
regionName = "kneePain"

# zoomedPklFile = 'zoomedGraph_Participant1_Eyes.pkl'
# regionName = "foreheadEyesPain"

# zoomedPklFile = 'zoomedGraph_Participant2_Knee.pkl'
# regionName = "kneepain"

# zoomedPklFile = 'zoomedGraph_Participant8_Knee.pkl'
# regionName = "kneepain"


savePlots = False
plotRegression = True
plotHighPainRegionAndTrigger = True

cutoffDays = 5

maxGapAllowed = 2

longPainStartMinus = 5
longPainStartPlus = 2

strainTriggerAmpMinus = 5
strainTriggerAmpPlus  = 2


if os.path.exists(regionName):
  shutil.rmtree(regionName)

os.mkdir(regionName)

with open(zoomedPklFile, 'rb') as f:
  zoomedSections = pkl.load(f)

relativeLocation                    = []
maxStrainNearHighPainStartTrigger   = []
maxStrainPeakToHighPainStartTrigger = []
longPainStartArray                  = []

for ind in range(0, len(zoomedSections)):

  zoomSectionData    = zoomedSections[ind]['data']
  zoomMaxStrainScore = zoomedSections[ind]['maxStrainScore']

  pain   = zoomSectionData[regionName].tolist()
  strain = zoomSectionData['regionSpecificstrain'].tolist()

  maxStrainIndex = zoomSectionData.index.get_loc(zoomSectionData.index[zoomSectionData['maxstrain'].notna().tolist()][0])
  minPainIndex   = zoomSectionData.index.get_loc(zoomSectionData.index[zoomSectionData['min'].notna().tolist()][0])
  maxPainIndex   = zoomSectionData.index.get_loc(zoomSectionData.index[zoomSectionData['max'].notna().tolist()][0])

  # maxPainAmp    = max(pain[maxPainIndex-2:maxPainIndex]) if len(pain[maxPainIndex-2:maxPainIndex]) else -1
  maxPainAmpIndexStr = maxPainIndex-3 if maxPainIndex-3 >= 0 else 0
  maxPainAmpIndexEnd = maxPainIndex+1 if maxPainIndex+1 < len(pain) else maxPainIndex
  maxPainAmp = np.median(pain[maxPainAmpIndexStr:maxPainAmpIndexEnd]) if len(pain[maxPainAmpIndexStr:maxPainAmpIndexEnd]) else -1
  
  if maxPainAmp == -1:
    relativeLocation.append(-1)
    maxStrainNearHighPainStartTrigger.append(-1)
    maxStrainPeakToHighPainStartTrigger.append(-1)
    longPainStartArray.append(-1)
    print("problem 1:", ind)
  else:    
    gap           = 0
    pos           = maxPainIndex
    longPainStart = maxPainIndex
    while (pos > 0) and (pain[pos] >= maxPainAmp or gap < maxGapAllowed):
      if pain[pos] >= maxPainAmp:
        longPainStart = pos
      pos -= 1
      if pain[pos] < maxPainAmp:
        gap += 1
      else:
        gap = 0

    strainTriggerAmpIndStr = longPainStart-strainTriggerAmpMinus if longPainStart-strainTriggerAmpMinus >= 0 else 0
    strainTriggerAmpIndEnd = longPainStart+strainTriggerAmpPlus if longPainStart+strainTriggerAmpPlus < len(strain) else longPainStart
    strainTriggerAmp       = max(strain[strainTriggerAmpIndStr:strainTriggerAmpIndEnd]) if len(strain[strainTriggerAmpIndStr:strainTriggerAmpIndEnd]) else -1
    strainTriggerAmpIndex = strainTriggerAmpIndStr + np.argmax(strain[strainTriggerAmpIndStr:strainTriggerAmpIndEnd]) if len(strain[strainTriggerAmpIndStr:strainTriggerAmpIndEnd]) else 0
    
    if strainTriggerAmp == -1:
    
      relativeLocation.append(-1)
      maxStrainNearHighPainStartTrigger.append(-1)
      maxStrainPeakToHighPainStartTrigger.append(-1)
      longPainStartArray.append(-1)
      print("problem 2:")
    
    else:
    
      relativeLocation.append(zoomMaxStrainScore)
      maxStrainNearHighPainStartTriggerVal = max(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)]) if len(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)]) else -1
      maxStrainNearHighPainStartTrigger.append(maxStrainNearHighPainStartTriggerVal)
      maxStrainPeakToHighPainStartTriggerVal = longPainStart - maxStrainIndex
      maxStrainPeakToHighPainStartTrigger.append(maxStrainPeakToHighPainStartTriggerVal)
      longPainStartArray.append(longPainStart)
      
      if savePlots and maxStrainNearHighPainStartTriggerVal != -1 and maxStrainPeakToHighPainStartTriggerVal >= -5 and maxStrainPeakToHighPainStartTriggerVal < 28 and longPainStart > 1:
        
        fig, ax1 = plt.subplots(1, 1, figsize=(22.9, 8.8))
        zoomSectionData[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].plot(ax=ax1, color = ['blue', 'red'])
        zoomSectionData[['max', 'min', 'maxstrain']].plot(ax=ax1, color = ['black', 'black', 'green'], linestyle='', marker='o', markersize = 10)
        
        zoomSectionData[['regionSpecificstrain', regionName]].plot(ax=ax1, color = ['blue', 'red'], linestyle='', marker='o')
        
        if plotHighPainRegionAndTrigger:
          
          longPeriodOfHighPain = [float('nan') for i in range(0, len(zoomSectionData))]
          for i in range(longPainStart, len(strain)):
            longPeriodOfHighPain[i] = maxPainAmp - 0.01
          zoomSectionData['longPeriodOfHighPain'] = longPeriodOfHighPain
          zoomSectionData[['longPeriodOfHighPain']].plot(ax=ax1, color = ['black'])
          
          strainTriggerAmpPos = [float('nan') for i in range(0, len(zoomSectionData))]
          for i in range(strainTriggerAmpIndStr, strainTriggerAmpIndEnd):
            strainTriggerAmpPos[i] = strainTriggerAmp + 0.01
          zoomSectionData['strainTriggerAmpPos'] = strainTriggerAmpPos
          zoomSectionData[['strainTriggerAmpPos']].plot(ax=ax1, color = ['green'])
          # strainTriggerAmpPos = [float('nan') for i in range(0, len(zoomSectionData))]
          # strainTriggerAmpPos[strainTriggerAmpIndex] = strainTriggerAmp + 0.026
          # zoomSectionData['strainTriggerAmpPos'] = strainTriggerAmpPos
          # zoomSectionData[['strainTriggerAmpPos']].plot(ax=ax1, color = ['purple'], linestyle='', marker='x')
        
        ax1.legend(['strainFiltered', 'painFiltered', 'maxPainPeak', 'minPainPeak', 'maxStrainPeak', 'strain', 'pain', 'highPainPeriod', 'strainTrigger'], loc="center left", bbox_to_anchor=(1, 0.5))
        # plt.title("Strain relative location: " + str(zoomMaxStrainScore))
        plt.title("Max strain peak to high pain start : " + str(longPainStart - maxStrainIndex) + " ; Max strain in the 5 days prior to high pain start : " + str(int(max(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)])*100)/100 if len(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)]) else -1))
        
        plt.savefig(os.path.join(regionName, regionName + '_' + str(longPainStart - maxStrainIndex) + '_' + str(int(max(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)])*100)/100 if len(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)]) else -1) + '_' + str(ind) + '.png'))


for i in range(0, len(maxStrainPeakToHighPainStartTrigger)):
  print(i, int(maxStrainPeakToHighPainStartTrigger[i]*100)/100, int(maxStrainNearHighPainStartTrigger[i]*100)/100)


indToRemove = np.where(np.logical_or(np.logical_or(np.logical_or(np.array(maxStrainNearHighPainStartTrigger) == -1, np.array(maxStrainPeakToHighPainStartTrigger) < -5), np.array(longPainStartArray) <= 1), np.array(maxStrainPeakToHighPainStartTrigger) >= 28))[0].tolist()

print("len(indToRemove):", len(indToRemove))

maxStrainPeakToHighPainStartTrigger = np.delete(maxStrainPeakToHighPainStartTrigger, indToRemove).tolist()
maxStrainNearHighPainStartTrigger   = np.delete(maxStrainNearHighPainStartTrigger, indToRemove).tolist()
relativeLocation                    = np.delete(relativeLocation, indToRemove).tolist()

fig3, axes = plt.subplots(nrows=1, ncols=2)

if False:
  from sklearn.linear_model import LinearRegression
  reg = LinearRegression().fit(np.array([maxStrainPeakToHighPainStartTrigger]).reshape(-1, 1), np.array([maxStrainNearHighPainStartTrigger]).reshape(-1, 1))
  regScore = reg.score(np.array([maxStrainPeakToHighPainStartTrigger]).reshape(-1, 1), np.array([maxStrainNearHighPainStartTrigger]).reshape(-1, 1))
  print("regression score:", regScore)
  pred = reg.predict(np.array([i for i in range(0, max(maxStrainPeakToHighPainStartTrigger))]).reshape(-1, 1))
  plt.plot([i for i in range(0, max(maxStrainPeakToHighPainStartTrigger))], pred)
else:
  axes[0].plot([cutoffDays + 0.1 for i in range(0, 11)], [i/10 for i in range(0, 11)])
  
axes[0].plot(maxStrainPeakToHighPainStartTrigger, maxStrainNearHighPainStartTrigger, '.')

belowOneWeek = np.array(maxStrainPeakToHighPainStartTrigger) < cutoffDays + 0.5
aboveOneWeek = np.array(maxStrainPeakToHighPainStartTrigger) >= cutoffDays + 0.5

axes[0].set(xlabel='maxStrainPeak to highPainStart nb of days', ylabel='maxStrain in the 5 days before highPainStart')

axes[1].boxplot([np.array(maxStrainNearHighPainStartTrigger)[belowOneWeek].tolist(), np.array(maxStrainNearHighPainStartTrigger)[aboveOneWeek].tolist()])
axes[1].set(xlabel='maxStrainPeak to highPainStart nb of days', ylabel='maxStrain in the 5 days before highPainStart')
axes[1].set_xticklabels(['belowOneWeek', 'aboveOneWeek'])

plt.show()


if plotRegression:

  fig3, axes = plt.subplots(nrows=1, ncols=1)

  axes.plot(relativeLocation, maxStrainPeakToHighPainStartTrigger, '.')
  axes.set(xlabel='relative location', ylabel='maxStrainPeak to highPainStart nb of days')

  from sklearn.linear_model import LinearRegression
  reg = LinearRegression().fit(np.array([relativeLocation]).reshape(-1, 1), np.array([maxStrainPeakToHighPainStartTrigger]).reshape(-1, 1))
  regScore = reg.score(np.array([relativeLocation]).reshape(-1, 1), np.array([maxStrainPeakToHighPainStartTrigger]).reshape(-1, 1))
  print("regression score:", regScore)
  pred = reg.predict(np.array([i/10 for i in range(0, 10)]).reshape(-1, 1))
  axes.plot([i/10 for i in range(0, 10)], pred)

  plt.show()
