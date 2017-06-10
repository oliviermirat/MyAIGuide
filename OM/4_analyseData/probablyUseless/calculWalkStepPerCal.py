import pickle
import numpy as np

input = open('localData3.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

walkcal=environment[:,27]
walksteps=environment[:,28]
print(len(walkcal),len(walksteps))

cond=walkcal!=0
walkcal=np.extract(cond,walkcal)
walksteps=np.extract(cond,walksteps)
print(len(walkcal),len(walksteps))

stepPerCal=walksteps/walkcal
print(len(stepPerCal))

print(np.mean(stepPerCal))