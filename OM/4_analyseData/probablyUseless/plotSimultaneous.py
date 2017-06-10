import pickle
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas
import math


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


def simuPlot(toPlot,labels,xaxis,fix=3.5):

	M=max(toPlot[0])

	plt.subplot(3,1,1)
	if (fix):
		plt.plot(xaxis,[fix]*len(xaxis))
	for idx,tp in enumerate(toPlot):
		m=max(tp)
		plt.plot(xaxis,tp*(M/m),label=labels[idx])
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

	plt.subplot(3,1,2)
	if (fix):
		plt.plot(xaxis,[fix]*len(xaxis))

	wind=7

	tpAccu=pandas.rolling_mean(toPlot[0],wind)
	M=np.nanmax(tpAccu)
	# plt.plot(xaxis- datetime.timedelta(days=10) ,tpAccu,label=labels[0])
	plt.plot(xaxis,tpAccu,label=labels[0])

	for idx,tp in enumerate(toPlot):
		if (idx):
			# tpAccu=createPastMoy(tp,[1,0.75,0.5,0.2,0.1,0.1,0.1,0.1])
			# tpAccu=createPastMoy(tp,[1,1,1,1,1,1,1,1])
			tpAccu=pandas.rolling_mean(tp,wind)
			m=np.nanmax(tpAccu)
			plt.plot(xaxis,tpAccu*(M/m),label=labels[idx])
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

	

	plt.subplot(3,1,3)
	tpAccu=pandas.rolling_mean(toPlot[0],wind)
	M=np.nanmax(tpAccu)
	plt.plot(xaxis- datetime.timedelta(days=12) ,tpAccu,label=labels[0])
	for idx,tp in enumerate(toPlot):
		if (idx):
			tpAccu=pandas.rolling_mean(tp,wind)
			m=np.nanmax(tpAccu)
			plt.plot(xaxis,tpAccu*(M/m),label=labels[idx])
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()
	# plt.plot(xaxis,toPlot[0],label='symp')
	# plt.plot(xaxis,maxx,label='maxx')
	# leg=plt.legend(loc='upper center', fontsize=9)
	# if leg:
	# 	leg.draggable()
	plt.show()


# Reload Data

input = open('localData3.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

mean=symptoms[:,3]
maxx=symptoms[:,4]
stress=environment[:,29]
mood=environment[:,30]
socquant=environment[:,31]

# Hands and Press

if (1):
	hands=symptoms[:,2]
	press=environment[:,9]+environment[:,10]
	# sport=environment[:,19]+environment[:,23]+environment[:,25]
	sport=environment[:,19]+environment[:,23]
	# climb=environment[:,15]
	climbViaMaxInt=environment[:,37]
	ubuntu=environment[:,34]/60
	cond=ubuntu<0
	ubuntu[cond]=0
	simuPlot([hands,press+ubuntu*1650*3,sport,climbViaMaxInt],
		['hands','press','othersport','climbViaMaxInt'],xaxis)

# Head and Manic Time

if (0):
	head=symptoms[:,1]
	manictime=environment[:,0]/(60*60)
	paper=environment[:,33]/60
	driving=environment[:,35]/60
	simuPlot([head,manictime+ubuntu+paper],['head','computer'],xaxis)

# Knees and steps and more

if (0):
	knees=symptoms[:,0]
	steps=environment[:,12]
	bike=environment[:,19]+environment[:,21]
	# steps+=bike*40
	steps+=bike*10
	# simuPlot([knees,steps,bike],['knees','steps','bike'],xaxis)
	simuPlot([knees,steps],['knees','steps'],xaxis)


# Soc Weight Mean and Max Pain

# simuPlot([mean,maxx,stress,mood,socquant],
# 	['mean','maxx','stress','mood','socquant'],xaxis,0)

