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

# zoomedPklFile = 'zoomedGraph_Participant8_Knee_LowestPain.pkl'
# regionName = "kneepain"

# zoomedPklFile = 'zoomedGraph_Participant8_Knee_RollingMean.pkl'
# regionName = "kneepain"

createFigs = False
if createFigs:
  plt.rcParams.update({'font.size': 12})

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
        fig.subplots_adjust(top=0.90)
        zoomSectionData[['regionSpecificstrain_RollingMean_MinMaxScaler', regionName + '_RollingMean_MinMaxScaler']].plot(ax=ax1, color = ['blue', 'red'])
        zoomSectionData[['max', 'min', 'maxstrain']].plot(ax=ax1, color = ['black', 'black', 'green'], linestyle='', marker='o', markersize = 10)
        
        zoomSectionData[['regionSpecificstrain', regionName]].plot(ax=ax1, color = ['blue', 'red'], linestyle='', marker='o')
        
        if plotHighPainRegionAndTrigger:
          
          longPeriodOfHighPain = [float('nan') for i in range(0, len(zoomSectionData))]
          for i in range(longPainStart, len(strain)):
            longPeriodOfHighPain[i] = maxPainAmp - 0.01
          zoomSectionData['longPeriodOfHighPain'] = longPeriodOfHighPain
          zoomSectionData[['longPeriodOfHighPain']].plot(ax=ax1, color = ['black'], linewidth=3)
          
          strainTriggerAmpPos = [float('nan') for i in range(0, len(zoomSectionData))]
          for i in range(strainTriggerAmpIndStr, strainTriggerAmpIndEnd):
            strainTriggerAmpPos[i] = strainTriggerAmp + 0.01
          zoomSectionData['strainTriggerAmpPos'] = strainTriggerAmpPos
          zoomSectionData[['strainTriggerAmpPos']].plot(ax=ax1, color = ['green'], linewidth=3)
          # strainTriggerAmpPos = [float('nan') for i in range(0, len(zoomSectionData))]
          # strainTriggerAmpPos[strainTriggerAmpIndex] = strainTriggerAmp + 0.026
          # zoomSectionData['strainTriggerAmpPos'] = strainTriggerAmpPos
          # zoomSectionData[['strainTriggerAmpPos']].plot(ax=ax1, color = ['purple'], linestyle='', marker='x')
        
        ax1.legend(['strainFiltered', 'painFiltered', 'maxPainPeak', 'minPainPeak', 'maxStrainPeak', 'strain', 'pain', 'highPainPeriod', 'strainTrigger'], loc="center left", bbox_to_anchor=(1, 0.5))
        if True:
          ax1.get_legend().remove()
        # plt.title("Strain relative location: " + str(zoomMaxStrainScore))
        plt.rcParams.update({'font.size': 18})
        plt.title("Max strain peak to high pain start : " + r"$\bf{" + str(longPainStart - maxStrainIndex) + "}$ ; Max strain in the 5 days prior and 2 days after the high pain period start : " + r"$\bf{" + str(int(max(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)])*100)/100 if len(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)]) else -1) + str("}$\n"))
        
        if createFigs:
          plt.savefig(os.path.join(regionName, regionName + '_' + str(longPainStart - maxStrainIndex) + '_' + str(int(max(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)])*100)/100 if len(strain[(longPainStart-longPainStartMinus if longPainStart-longPainStartMinus >= 0 else 0):(longPainStart+longPainStartPlus if longPainStart+longPainStartPlus < len(strain) else longPainStart)]) else -1) + '_' + str(ind) + '.svg'))
        plt.rcParams.update({'font.size': 12})


for i in range(0, len(maxStrainPeakToHighPainStartTrigger)):
  print(i, int(maxStrainPeakToHighPainStartTrigger[i]*100)/100, int(maxStrainNearHighPainStartTrigger[i]*100)/100)


print("maxStrainNearHighPainStart == -1 : Removed nb : ",   len(np.where(np.array(maxStrainNearHighPainStartTrigger) == -1)[0].tolist()))
print("longPainStart <= 1 : Removed nb : ",                 len(np.where(np.array(longPainStartArray) <= 1)[0].tolist()))
print("maxStrainPeakToHighPainStart < -5 : Removed nb : ",  len(np.where(np.array(maxStrainPeakToHighPainStartTrigger) < -5)[0].tolist()))
print("maxStrainPeakToHighPainStart >= 28 : Removed nb : ", len(np.where(np.array(maxStrainPeakToHighPainStartTrigger) >= 28)[0].tolist()))

indToRemove = np.where(np.logical_or(np.logical_or(np.logical_or(np.logical_or(np.array(maxStrainNearHighPainStartTrigger) == -1, np.array(relativeLocation) < 0), np.array(maxStrainPeakToHighPainStartTrigger) < -5), np.array(longPainStartArray) <= 1), np.array(maxStrainPeakToHighPainStartTrigger) >= 28))[0].tolist()

print("len(indToRemove):", len(indToRemove))

maxStrainPeakToHighPainStartTrigger = np.delete(maxStrainPeakToHighPainStartTrigger, indToRemove).tolist()
maxStrainNearHighPainStartTrigger   = np.delete(maxStrainNearHighPainStartTrigger, indToRemove).tolist()
relativeLocation                    = np.delete(relativeLocation, indToRemove).tolist()

if createFigs:
  fig, axes = plt.subplots(figsize=(6, 1.8), dpi=300, nrows=1, ncols=2)
  fig.subplots_adjust(left=0.16, bottom=0.24, right=0.98, top=0.98, wspace=0.4)
else:
  fig, axes = plt.subplots(nrows=1, ncols=2)

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

if not(createFigs):
  axes[0].set(xlabel='maxStrainPeak to highPainStart nb of days', ylabel='maxStrain in the 5 days before highPainStart')
axes[1].boxplot([np.array(maxStrainNearHighPainStartTrigger)[belowOneWeek].tolist(), np.array(maxStrainNearHighPainStartTrigger)[aboveOneWeek].tolist()])
if not(createFigs):
  axes[1].set(xlabel='maxStrainPeak to highPainStart nb of days', ylabel='maxStrain in the 5 days before highPainStart')
axes[1].set_xticklabels(['below\n5 days', 'above\n5 days'])

if createFigs:
  plt.savefig('strainBuildUpFastRiseAndTriggerGraph.svg')
  plt.close()
else:
  plt.show()


if plotRegression:
  
  if createFigs:
    fig3, axes = plt.subplots(figsize=(3, 2.3), dpi=300, nrows=1, ncols=1)
    fig3.subplots_adjust(left=0.4, bottom=0.28, right=0.98, top=0.98, wspace=0.4)
  else:
    fig3, axes = plt.subplots(nrows=1, ncols=1)

  axes.plot(relativeLocation, maxStrainPeakToHighPainStartTrigger, '.')
  axes.set(xlabel='Relative location', ylabel='MaxStrainPeak\nto highPainStart\nnumber of days')

  from sklearn.linear_model import LinearRegression
  reg = LinearRegression().fit(np.array([relativeLocation]).reshape(-1, 1), np.array([maxStrainPeakToHighPainStartTrigger]).reshape(-1, 1))
  regScore = reg.score(np.array([relativeLocation]).reshape(-1, 1), np.array([maxStrainPeakToHighPainStartTrigger]).reshape(-1, 1))
  print("regression score:", regScore)
  pred = reg.predict(np.array([i/10 for i in range(0, 10)]).reshape(-1, 1))
  axes.plot([i/10 for i in range(0, 10)], pred)

  if createFigs:
    plt.savefig('relativeLocationCorrelation.svg')
    plt.close()
  else:
    plt.show()
