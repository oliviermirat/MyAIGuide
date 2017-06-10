import pickle
import findOptimalShift as optShift
import numpy as np
import matplotlib.pyplot as plt

input = open('localData3.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

knees=symptoms[:,0]
steps=environment[:,12]
bike=environment[:,19]+environment[:,21]
# steps+=bike*40
steps+=bike*10

[shift,maxx]=optShift.findOptimalShift(knees,steps,xaxis)
print(shift,maxx)
