# This scripts assumes that the dataframe has been created and saved in data.txt

import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from dataFrameUtilities import selectTime, selectColumns, addRollingMeanColumns

input = open('data.txt', 'rb')
data = pickle.load(input)
input.close()

timeSelected = selectTime(data, '2016-09-01', '2019-10-20')

pain = selectColumns(timeSelected, ['kneePain'])
pain = addRollingMeanColumns(pain, ['kneePain'], 21)

env = addRollingMeanColumns(timeSelected, ['steps','denivelation'], 21)
envRollingMean = selectColumns(env, ['stepsRollingMean','denivelationRollingMean'])
envBrut = selectColumns(env, ['steps','denivelation'])

fig, axes = plt.subplots(nrows=3, ncols=1)

pain.plot(ax=axes[0])
envBrut.plot(ax=axes[1])
envRollingMean.plot(ax=axes[2])

plt.legend(loc='best')
plt.show()
