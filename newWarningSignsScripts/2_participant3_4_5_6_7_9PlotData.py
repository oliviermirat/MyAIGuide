import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

participant_ids = [3, 4, 5, 6, 7, 9]

columnnamesId = {3 : ["googlefitsteps", "kneepain"],     # not enough values for "happiness"
                 4 : ["steps", "kneepain", "elbowpain"], # not enough values for "happiness"
                 5 : ["steps", "anklepain"],
                 6 : ["googlefitsteps", "kneepain"],
                 7 : ["steps", "hippain", "shoulderpain", "happiness"],
                 9 : ["steps", "kneepain", "happiness"]}

colors = ['red', 'blue', 'purple', 'black', 'green', 'yellow']

for participant_id in participant_ids:
  
  print("\nPlotting dataframe for participant " + str(participant_id))
                 
  input = open("../data/preprocessed/preprocessedDataParticipant" + str(participant_id) + ".txt", "rb")
  data = pickle.load(input)
  input.close()

  fig, axes = plt.subplots(nrows=len(columnnamesId[participant_id]) + 1, ncols=1)
  fig.suptitle("Participant: " + str(participant_id))

  for idx, parameter in enumerate(columnnamesId[participant_id]):
    axes[idx].plot(data[parameter], label=parameter, color=colors[idx])

  scaler = MinMaxScaler()
  data[columnnamesId[participant_id]] = scaler.fit_transform(data[columnnamesId[participant_id]])
  for idx, parameter in enumerate(columnnamesId[participant_id]):
      axes[len(columnnamesId[participant_id])].plot(data[parameter], label=parameter, color=colors[idx])

  for idx in range(0, len(columnnamesId[participant_id]) + 1):
    axes[idx].legend(loc='upper right')
  
  leg = plt.legend(loc="best")
  leg.set_draggable(True)
  plt.show()
