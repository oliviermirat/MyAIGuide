from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

plotWithScaling = False

def prepareForPlotting(data, region, minpeaks, maxpeaks):
  
  data['painAscending']  = data[region + '_RollingMean_MinMaxScaler']
  data['painDescending'] = data[region + '_RollingMean_MinMaxScaler']
  data['maxstrain2']     = data['maxstrain']
  
  allPeaks = np.concatenate((minpeaks, maxpeaks))
  ascending = True
  ascendingElement  = [0 for i in range(0, len(data))]
  descendingElement = [0 for i in range(0, len(data))]
  if len(allPeaks) and min(allPeaks) in maxpeaks:
    ascending = False
  if len(allPeaks):
    for i in range(min(allPeaks), max(allPeaks)):
      if i in maxpeaks:
        ascendingElement[i] = 0
        # descendingElement[i-1] = 1
        ascending = False
        firstElem = True
      if i in minpeaks:
        descendingElement[i] = 0
        # ascendingElement[i-1] = 1
        ascending = True
        firstElem = True
      if not(firstElem):
        if ascending:
          ascendingElement[i] = 1
        else:
          descendingElement[i] = 1
      else:
        firstElem = False
       
    
    data['painAscending'][[ind for ind, val in enumerate(descendingElement) if val or ind < min(allPeaks) or ind > max(allPeaks)]] = float('nan')
    data['painDescending'][[ind for ind, val in enumerate(ascendingElement) if val or ind < min(allPeaks) or ind > max(allPeaks)]] = float('nan')
    data['maxstrain2'][[ind for ind in range(0, len(data)) if ind < min(allPeaks) or ind > max(allPeaks)]] = float('nan')
    
    data = data.drop(columns=[region + '_RollingMean_MinMaxScaler', 'max', 'min', 'maxstrain', 'regionSpecificstrain_RollingMean_MinMaxScaler'])
  
  return data


def plottingOptions(axes, axesNum, text, legendsText, locLegend, sizeLegend, createFigs=False, takeAxesNum=True):
  if createFigs and not(takeAxesNum):
    axis = axes
  else:
    axis = axes[axesNum]
  axis.set_ylim([0, 1])
  axis.yaxis.set_major_locator(MaxNLocator(1))
  if not(createFigs):
    if legendsText:
      axis.legend(legendsText, loc=locLegend, bbox_to_anchor=(1, 0.5)) #, prop={'size': sizeLegend})
    else:
      if plotWithScaling:
        axis.legend(loc=locLegend, prop={'size': sizeLegend})
      else:
        axis.legend(loc=locLegend, bbox_to_anchor=(1, 0.5)) #, prop={'size': sizeLegend})
    axis.title.set_text(text)
    if plotWithScaling:
      axis.title.set_fontsize(5)
    axis.title.set_position([0.5, 0.93])
  else:
    axis.title.set_fontsize(12)
    axis.title.set_text(text)
    if axis and axis.get_legend():
      axis.get_legend().remove()
  axis.get_xaxis().set_visible(False)


def plotMaxStrainLocationInMinMaxCycle(maxstrainScores, nbDescendingDays, nbAscendingDays, createFigs):
  descendingWeight = len(maxstrainScores) * ((nbDescendingDays / (nbDescendingDays + nbAscendingDays)) / 5)
  ascendingWeight  = len(maxstrainScores) * ((nbAscendingDays  / (nbDescendingDays + nbAscendingDays)) / 5)
  if createFigs:
    fig = plt.figure(figsize=(3.5, 2.8), dpi=300)
    fig.subplots_adjust(left=0.16, bottom=0.16, right=0.98, top=0.98)
    ax = plt.gca()
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.xaxis.set_major_locator(MaxNLocator(3))
    plt.xlabel('Relative location')
    plt.ylabel('Number of occurrences')
  plt.hist([(i-4.5)/5 for i in range(0, 10)], 10, weights=[descendingWeight for i in range(0, 5)]+[ascendingWeight for i in range(0, 5)], alpha=0.5, label='Theoritical if randomly distributed', range=(-1, 1))
  plt.hist(maxstrainScores, alpha=0.5, label='Observed', range=(-1, 1))
  if not(createFigs):
    plt.legend()
    plt.title("Locations of maxStrain in the min/max pain cycle: Theoritical if randomly distributed vs Observed")
    plt.show()
  else:
    plt.savefig('./folderToSaveFigsIn/' + 'maxStrainLocationInMinMaxPainCycle.svg')
    plt.close()


def plotMaxPain(createFigs, painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain, painMinMaxAmplitudes):
  print(str(len(painMinMaxAmplitudesNoStrain)) + " pain amplitudes (out of " + str(len(painMinMaxAmplitudesNoStrain) + len(painMinMaxAmplitudesWtStrain)) + ") had no strain peak preceding them ( " + str(( len(painMinMaxAmplitudesNoStrain) / (len(painMinMaxAmplitudesNoStrain) + len(painMinMaxAmplitudesWtStrain)) )*100) + " % )")
  if createFigs:
    fig = plt.figure(figsize=(3.5, 2.8), dpi=300)
    fig.subplots_adjust(left=0.16, bottom=0.18, right=0.98, top=0.98)
    plt.xlabel('Pain peak amplitude (normalized)')
    plt.ylabel('Number of occurrences')
  plt.hist(painMinMaxAmplitudesWtStrain, range=(min(painMinMaxAmplitudes), max(painMinMaxAmplitudes)), alpha=0.5, label='Max strain PRESENT in ascending pain period')
  plt.hist(painMinMaxAmplitudesNoStrain, range=(min(painMinMaxAmplitudes), max(painMinMaxAmplitudes)), alpha=0.5, label='Max strain ABSENT in ascending pain period')
  print("painMinMaxAmpWtVsWithoutStrain, ttest:", stats.ttest_ind(painMinMaxAmplitudesWtStrain, painMinMaxAmplitudesNoStrain))
  if not(createFigs):
    plt.legend()
    plt.title("Histograms of amplitudes of maximum pain peaks when:")
    plt.show()
  else:
    plt.savefig('./folderToSaveFigsIn/' + 'maxPainPeakAmplitudeHistogram.svg')
    plt.close()
