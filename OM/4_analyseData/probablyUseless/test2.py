import pickle
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas
import math
from sklearn import preprocessing

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


def putLegend():
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

def findOptimalShift(symptom,envir,xaxis):

	# Plot Raw data
	M=np.nanmax(symptom)
	m=np.nanmax(envir)
	plt.subplot(411)
	plt.plot(symptom,label='symptom')
	plt.plot(envir*(M/m),label='environment')
	putLegend()

	# Calculates rolling mean
	window=7
	symptom=pandas.rolling_mean(symptom,window)
	envir=pandas.rolling_mean(envir,window)
	symptom=symptom[window-1:len(symptom)]
	envir=envir[window-1:len(envir)]
	# Plotting Rolling Mean
	M=np.nanmax(symptom)
	m=np.nanmax(envir)
	plt.subplot(412)
	plt.plot(symptom,label='symptom')
	plt.plot(envir*(M/m),label='environment')
	putLegend()

	# Normalize and Scale
	combin=np.zeros((len(symptom),2))
	combin[:,0]=symptom
	combin[:,1]=envir
	combin[:,0] = preprocessing.normalize(combin[:,0])
	combin[:,1] = preprocessing.normalize(combin[:,1])
	combin = preprocessing.normalize(combin)
	combin=preprocessing.scale(combin)
	plt.subplot(413)
	plt.plot(combin)

	# Calculates Optimal Correlation
	x=combin[:,0]
	y=combin[:,1]
	corr=np.correlate(x, np.hstack((y[1:], y)), mode='valid')
	# corr=np.correlate(x,y,"full")
	shift=int(np.argmax(corr[0:100]))
	plt.subplot(414)
	plt.plot(corr)
	plt.show()

	return [shift,corr[shift]]

[shift,maxx]=findOptimalShift(knees,steps,xaxis)

print(shift,maxx)
