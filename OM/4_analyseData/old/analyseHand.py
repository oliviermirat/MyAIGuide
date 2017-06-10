import pickle
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()

symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]
hands=symptoms[:,2]
press=environment[:,9]+environment[:,10]


def createPastMoy(data,weigths):
	nbDays=len(weigths)
	n=len(data)
	# m=len(data[1])
	m=1
	past=np.zeros((n,m))
	for i in range(nbDays,n):
		for j in range(1,nbDays+1):
			past[i,:]+=data[i-j]*weigths[j-1]
		past[i,:]=past[i,:]/sum(weigths)
	return past


def simuPlot(hands,press,labelSymp):

	rollingNb=2
	dividBy=5000

	handmean=pandas.rolling_mean(hands,rollingNb)

	envi=[]
	for d in press:
		dividBy=max(d)*4.5
		pressmean=pandas.rolling_mean(d/dividBy,rollingNb)
		envi.append(pressmean)
	# xaxisminus=np.delete(xaxis,0)

	plt.subplot(3,1,1)
	plt.plot(xaxis,hands,label='hand')
	plt.plot(xaxis,press/dividBy,label='press')
	plt.plot(xaxis,[3.5]*len(xaxis))
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

	plt.subplot(3,1,2)
	plt.plot(xaxis,handmean,label='hand')
	plt.plot(xaxis,pressmean,label='press')
	plt.plot(xaxis,[3.5]*len(xaxis))
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

	plt.subplot(3,1,3)
	plt.plot(xaxis,hands,label='hand')
	plt.plot(xaxis,createPastMoy(press/dividBy,[1,0.75,0.5,0.2,0.1,0.1,0.1,0.1]),
		label='press')
	plt.plot(xaxis,[3.5]*len(xaxis))
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

	plt.show()


simuPlot(hands,[press],['press'])

