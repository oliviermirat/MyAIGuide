import pandas as pd
import numpy as np
import math

stats = pd.DataFrame(columns=['Participant', 'Range', 'Number of sets of model parameters tested', 'Percent of ratios above 1', 'Percent of ratios significantly above 1', 'Percent of ratios significantly below 1'])

idx = 0

pd.set_option('display.max_rows', 1000)

for participantId, participantData in enumerate(["participant1DifferentParameters.pkl", "participant2DifferentParameters.pkl", "participant8DifferentParameters_lowestPain.pkl", "participant8DifferentParameters_rollingMean.pkl"]):
  
  print("")
  print(participantData)
  
  stats.loc[idx] = ['', '', '', '', '', '']
  idx += 1
  
  data = pd.read_pickle(participantData)
  
  for rangeId in [1, 2, 3]:
    
    ratio         = data["ratio" + str(rangeId)].tolist()
    
    nb_ratioAbove1  = np.sum(np.array(ratio) > 1)
    nb_ratioSignificant = np.sum(np.array(data["poissonPValue" + str(rangeId)].tolist()) <= 0.05)
    
    dataRatioAbove1  = data.copy().drop([i for i, val in enumerate(np.array(ratio) <  1) if val])
    dataRatioBellow1 = data.copy().drop([i for i, val in enumerate(np.array(ratio) >= 1) if val])
    nb_ratioSignificant2 = np.sum(np.array(dataRatioAbove1["poissonPValue"  + str(rangeId)].tolist()) <= 0.05)
    nb_ratioSignificant3 = np.sum(np.array(dataRatioBellow1["poissonPValue" + str(rangeId)].tolist()) <= 0.05)
    
    print("rangeId:", rangeId, " : ratios percent above 1: ", nb_ratioAbove1,       len(data),            " : ", nb_ratioAbove1 / len(data))
    print("rangeId:", rangeId, " : signif naive above 1: ", nb_ratioSignificant,  len(data),            " : ", nb_ratioSignificant / len(data))
    print("rangeId:", rangeId, " : signif above 1: ", nb_ratioSignificant2, len(dataRatioAbove1), " : ", nb_ratioSignificant2 / len(dataRatioAbove1))
    print("rangeId:", rangeId, " : signif below 1: ", nb_ratioSignificant3, len(dataRatioBellow1), " : ", nb_ratioSignificant3 / len(dataRatioBellow1))
    
    if participantId == 0:
      participantLabel = 'Participant 1'
    elif participantId == 1:
      participantLabel = 'Participant 2'
    elif participantId == 2:
      participantLabel = 'Participant 8 (Lowest pain)'
    else:
      participantLabel = 'Participant 8 (Rolling mean)'
    stats.loc[idx] = [participantLabel, rangeId, len(data), round(nb_ratioAbove1 / len(data), 2), round(nb_ratioSignificant2 / len(dataRatioAbove1), 2), round(nb_ratioSignificant3 / len(dataRatioBellow1), 2) if not(math.isnan(nb_ratioSignificant3 / len(dataRatioBellow1))) else 'NaN']
    idx += 1

print(stats)
stats.to_excel('stats.xls')
