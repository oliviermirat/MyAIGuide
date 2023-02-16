import sys
sys.path.insert(1, '../src/MyAIGuide/utilities')

import pickle
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

import pandas as pd
import seaborn as sns
import numpy as np

import peakAnalysis_plot

plotMaxInOtherRegion = False
mult = False

inputt = open("peaksData.txt", "rb")
data = pickle.load(inputt)
inputt.close()

if 'Knee' in data:
  [maxStressScoresKnee, totDaysAscendingPainKnee, totDaysDescendingPainKnee, dataKnee, data2Knee, stressMinMaxAmplitudesKnee, painMinMaxAmplitudesKnee] = data['Knee']
if 'Arm' in data:
  [maxStressScoresArm, totDaysAscendingPainArm, totDaysDescendingPainArm, dataArm, data2Arm, stressMinMaxAmplitudesArm, painMinMaxAmplitudesArm] = data['Arm']
if 'Head' in data:
  [maxStressScoresHead, totDaysAscendingPainHead, totDaysDescendingPainHead, dataHead, data2Head, stressMinMaxAmplitudesHead, painMinMaxAmplitudesHead] = data['Head']

if 'Arm' in data:
  maxStressScores = np.concatenate((np.concatenate((maxStressScoresKnee, maxStressScoresArm)), maxStressScoresHead))
  print("ascending: ", totDaysAscendingPainKnee + totDaysAscendingPainArm + totDaysAscendingPainHead)
  print("descending:" , totDaysDescendingPainKnee + totDaysDescendingPainArm + totDaysDescendingPainHead)
else:
  maxStressScores = np.concatenate((maxStressScoresKnee, maxStressScoresHead))
  print("ascending: ", totDaysAscendingPainKnee + totDaysAscendingPainHead)
  print("descending:" , totDaysDescendingPainKnee + totDaysDescendingPainHead)

print("maxStressScores: ", maxStressScores)
maxStressScores = [val for val in maxStressScores if not(np.isnan(val))]
print("maxStressScores: ", maxStressScores)
print("bad values: ", [val for val in maxStressScores if not(val >= -1 and val <= 1)])
print("len before: ", len(maxStressScores))
maxStressScores = [val if val >= -1 and val <= 1 else 1 for val in maxStressScores]
print("len after: ", len(maxStressScores))

if 'Arm' in data:
  fig, axes = plt.subplots(nrows=3, ncols=1)
  for ind, [region, data2] in enumerate([['Knee', data2Knee], ['Arm', data2Arm], ['Head', data2Head]]):
    data2.plot(ax=axes[ind])
    peakAnalysis_plot.plottingOptions(axes, ind, region, ['painAscending', 'painDescending', 'PeakStress'], 'center left', 8)
else:
  fig, axes = plt.subplots(nrows=2, ncols=1)
  for ind, [region, data2] in enumerate([['Knee', data2Knee], ['Head', data2Head]]):
    data2.plot(ax=axes[ind])
    peakAnalysis_plot.plottingOptions(axes, ind, region, ['painAscending', 'painDescending', 'PeakStress'], 'center left', 8)
plt.show()

plt.hist(maxStressScores)
plt.show()
