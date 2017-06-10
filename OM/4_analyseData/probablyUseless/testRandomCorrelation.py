import pickle
import findOptimalShift as optShift
import numpy as np

input = open('localData3.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]
knees=symptoms[:,0]

noise = np.random.normal(0,1,len(knees))
[shift,maxx]=optShift.findOptimalShift(knees,noise,xaxis,0)
print(shift,maxx)

Fs = 100
f = 5
sample = len(knees)
x = np.arange(sample)
y = np.sin(2 * np.pi * f * x / Fs)
[shift,maxx]=optShift.findOptimalShift(knees,y,xaxis,0)
print(shift,maxx)
