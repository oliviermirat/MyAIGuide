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
head=symptoms[:,1]
manictime=environment[:,0]

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

rollingNb=2
headmean=pandas.rolling_mean(head,rollingNb)
manicmean=pandas.rolling_mean(manictime/2,rollingNb)
# xaxisshift=xaxis+datetime.timedelta(20,0)
xaxisminus=np.delete(xaxis,0)
headmeandiff=np.diff(headmean)
manicmeandiff=np.diff(manicmean)

plt.subplot(3,1,1)
plt.plot(xaxis,head,label='head')
plt.plot(xaxis,manictime/2,label='manictime')
plt.plot(xaxis,[3.5]*len(xaxis))
leg=plt.legend(loc='upper center', fontsize=9)
if leg:
	leg.draggable()

plt.subplot(3,1,2)
plt.plot(xaxis,headmean,label='head')
plt.plot(xaxis,manicmean,label='manictime')
plt.plot(xaxis,[3.5]*len(xaxis))
leg=plt.legend(loc='upper center', fontsize=9)
if leg:
	leg.draggable()


plt.subplot(3,1,3)
plt.plot(xaxis,head,label='head')
plt.plot(xaxis,createPastMoy(manictime/2,[1,0.75,0.5,0.2,0.1,0.1,0.1,0.1]),
	label='manictime')
plt.plot(xaxis,[3.5]*len(xaxis))
leg=plt.legend(loc='upper center', fontsize=9)
if leg:
	leg.draggable()


# plt.subplot(3,1,3)
# plt.plot(xaxisminus,headmeandiff,label='head')
# plt.plot(xaxisminus,manicmeandiff,label='manictime')
# plt.plot(xaxis,[0]*len(xaxis))
# leg=plt.legend(loc='upper center', fontsize=9)
# if leg:
# 	leg.draggable()



plt.show()