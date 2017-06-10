import pickle
import numpy as np
import matplotlib.pyplot as plt
import math

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()

symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

def createPastMoy(data,nbDays):
	n=len(data)
	m=len(data[1])
	past=np.zeros((n,m))
	for i in range(nbDays,n):
		for j in range(1,nbDays+1):
			past[i,:]+=data[i-j]
		past[i,:]=past[i,:]/nbDays
	return past

def extract(cond,nEnv,envi):
	cond=np.array([cond,]*nEnv).transpose()
	out=np.extract(cond,envi)
	out=out.reshape((int(len(out)/nEnv), nEnv))
	return out

def defineGroup(envi,symp,thres):
	groups=[]
	n=len(thres)
	nEnv=len(envi[0])

	cond=symp<=thres[0]
	groups.append(extract(cond,nEnv,envi))

	for i in range(1,n):
		cond=(symp>thres[i-1])&(symp<=thres[i])
		groups.append(extract(cond,nEnv,envi))
	
	cond=symp>thres[n-1]
	groups.append(extract(cond,nEnv,envi))
	
	return groups

def chooseAndPlot(groups,cols):
	for idx, g in enumerate(groups):
		plt.plot(g[:,cols[0]], g[:,cols[1]], '.', label=str(idx))
		leg=plt.legend(loc='upper center', shadow=True)
		if leg:
			leg.draggable()
	plt.show()

def oneVariableCorrelation(envi,symp):
	plt.plot(symp,envi)

def sympAllEnvVar(envi,symp,lab):
	n=len(envi[0])
	m=math.ceil(math.sqrt(n))
	for i in range(0,n):
		plt.subplot(m,m-1,i+1)
		plt.plot(symp,envi[:,i],'.',label=lab[i])
		leg=plt.legend(loc='upper center', fontsize=9)
		if leg:
			leg.draggable()
	plt.show()


labelEnv=['manicTimeDur','alpiskidur','climbdur','downskidur','mtbikedur',
'roadbikedur','swimdur','viadur','walkdur','nbkeys','nbclicks',
'totcal','totsteps','alpiskical','alpiskisteps','climbcal','climbsteps',
'downskical','downskisteps','mtbikecal','mtbikesteps','roadbikecal',
'roadbikesteps','swimcal','swimsteps','viacal','viasteps','walkcal',
'walksteps','stress','mood','socquant','weight','paper','ubuntu',
'driving','store']

labelSymp=['Knees','Head','Hands']

past=createPastMoy(environment,3)

# groupK=defineGroup(past,symptoms[:,0],[2.9,3.9])
# chooseAndPlot(groupK,[12,28])

sympAllEnvVar(environment,symptoms[:,2],labelEnv)
