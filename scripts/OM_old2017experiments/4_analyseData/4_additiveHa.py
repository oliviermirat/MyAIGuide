import pickle

import additiveModel as addMod

input = open("localData.txt", "rb")
localData = pickle.load(input)
input.close()
symptoms = localData[0]
environment = localData[1]
xaxis = localData[2]

cond = environment[:, 34] < 0
environment[cond, 34] = 0

maxx = max(environment[:, 37])
minn = min(i for i in environment[:, 37] if i > 0)
minn -= 1
environment[:, 37] = environment[:, 37] - minn
cond = environment[:, 37] < 0
environment[cond, 37] = 0

averagingwindow = 7

select = [[9, 1], [10, 2], [34, 3.5], [37, 2.5], [19, 0.5], [23, 0.5]]
labels = ["Hands", "keys", "clicks", "ubuntu", "climb", "bike", "swim"]

addMod.additiveModel(2, select, labels, symptoms, environment, xaxis, averagingwindow)
