import pickle
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas


def putLegend():
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()

def putThres(fix,xaxis):
	if (fix):
		plt.plot(xaxis,[fix]*len(xaxis))

def simuPlot(toPlot,labels,xaxis,fix=3.5):

	M=max(toPlot[0])

	plt.subplot(3,1,1)
	putThres(fix,xaxis)
	for idx,tp in enumerate(toPlot):
		m=max(tp)
		plt.plot(xaxis,tp*(M/m),label=labels[idx])
	putLegend()

	# plt.subplot(3,1,2)
	# wind=30
	# symp=toPlot[0]
	# sympmax=pandas.rolling_max(symp,wind)
	# sympmax[0:wind]=sympmax[31]
	# symp=symp/sympmax
	# toPlot[0]=symp
	# putThres(fix,xaxis)
	# for idx,tp in enumerate(toPlot):
	# 	m=max(tp)
	# 	plt.plot(xaxis,tp*(M/m),label=labels[idx])
	# putLegend()

	plt.subplot(3,1,2)
	putThres(fix,xaxis)
	wind=7
	tpAccu=pandas.rolling_mean(toPlot[0],wind)
	M=np.nanmax(tpAccu)
	plt.plot(xaxis,tpAccu,label=labels[0])
	for idx,tp in enumerate(toPlot):
		if (idx):
			tpAccu=pandas.rolling_mean(tp,wind)
			m=np.nanmax(tpAccu)
			plt.plot(xaxis,tpAccu*(M/m),label=labels[idx])
	putLegend()

	# plt.subplot(3,1,3)
	# tpAccu=pandas.rolling_mean(toPlot[0],wind)
	# M=np.nanmax(tpAccu)
	# plt.plot(xaxis- datetime.timedelta(days=12) ,tpAccu,label=labels[0])
	# for idx,tp in enumerate(toPlot):
	# 	if (idx):
	# 		tpAccu=pandas.rolling_mean(tp,wind)
	# 		m=np.nanmax(tpAccu)
	# 		plt.plot(xaxis,tpAccu*(M/m),label=labels[idx])
	# putLegend()

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
		['hands','press','othersport','climbViaMaxInt'],xaxis,0)

# Head and Manic Time

if (1):
	head=symptoms[:,1]
	manictime=environment[:,0]/(60*60)
	paper=environment[:,33]/60
	driving=environment[:,35]/60
	simuPlot([head,manictime+ubuntu+paper],['head','computer'],xaxis)

# Knees and steps and more

if (1):
	knees=symptoms[:,0]
	steps=environment[:,12]
	bike=environment[:,19]+environment[:,21]
	steps+=bike*11
	simuPlot([knees,steps],['knees','steps'],xaxis)



