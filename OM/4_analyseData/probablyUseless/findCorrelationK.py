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

for i in range(1,60):
	[shift,maxx]=optShift.testCorrel(0,[[12,1],[19,i],[21,i]],symptoms,environment,xaxis)
	print(i,shift,maxx)

i=11
[shift,maxx]=optShift.testCorrel(0,[[12,1],[19,i],[21,i]],symptoms,environment,xaxis,1)
print(i,shift,maxx)