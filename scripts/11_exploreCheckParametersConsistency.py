import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 1000)

for participantData in ["participant1DifferentParameters.pkl", "participant2DifferentParameters.pkl", "participant8DifferentParameters.pkl"]:
  
  print("")
  print(participantData)
  
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

