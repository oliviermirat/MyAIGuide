import numpy as np
import matplotlib.pyplot as plt
import pandas
from sklearn import preprocessing


def putLegend():
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()


def findOptimalShift(symptom,envir,xaxis,pl=1):

	# Plot Raw data
	M=np.nanmax(symptom)
	m=np.nanmax(envir)
	plt.subplot(411)
	if (pl):
		plt.plot(symptom,label='symptom')
		plt.plot(envir*(M/m),label='environment')
		putLegend()

	# Calculates rolling mean
	window=7
	symptom=pandas.rolling_mean(symptom,window)
	envir=pandas.rolling_mean(envir,window)
	# symptom=pandas.DataFrame(symptom).rolling(window=window,center=False).mean()
	# envir=pandas.DataFrame(envir).rolling(window=window,center=False).mean()
	symptom=symptom[window-1:len(symptom)]
	envir=envir[window-1:len(envir)]
	# Plotting Rolling Mean
	M=np.nanmax(symptom)
	m=np.nanmax(envir)
	if (pl):
		plt.subplot(412)
		plt.plot(symptom,label='symptom')
		plt.plot(envir*(M/m),label='environment')
		putLegend()

	# Normalize and Scale
	combin=np.zeros((len(symptom),2))
	combin[:,0]=symptom
	combin[:,1]=envir
	combin[:,0] = preprocessing.normalize([combin[:,0]])
	combin[:,1] = preprocessing.normalize([combin[:,1]])
	combin = preprocessing.normalize(combin)
	combin=preprocessing.scale(combin)
	if (pl):
		plt.subplot(413)
		plt.plot(combin)

	# Calculates Optimal Correlation
	x=combin[:,0]
	y=combin[:,1]
	corr=np.correlate(x, np.hstack((y[1:], y)), mode='valid')
	# corr=np.correlate(x,y,"full")
	# shift=int(np.argmax(corr[0:100]))
	shift=int(np.argmax(corr[0:100]))
	if (pl):
		plt.subplot(414)
		plt.plot(corr)
		plt.show()

	return [shift,corr[shift]]


def testCorrel(sympNum,enviInfo,symptoms,environment,xaxis,show=0):
	sympt=symptoms[:,sympNum]
	zeros=np.zeros((len(symptoms),5))
	envir=zeros[:,0]
	for info in enviInfo:
		numCol=info[0]
		coeff=info[1]
		envir+=coeff*environment[:,numCol]
	[shift,maxx]=findOptimalShift(sympt,envir,xaxis,show)
	return [shift,maxx]
