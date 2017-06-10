import pickle
import additiveModel as addMod

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]

environment[:,0]=environment[:,0]+environment[:,34]*60 # Add Ubuntu time to Computer Time #
environment[:,35]=environment[:,35]+0.75*environment[:,38] # Add riding car to driving time #
xaxis=localData[2]

averagingwindow=7

select=[[0,1],[35,0.1]]
labels=['Head','Computer Time','Driving']

addMod.additiveModel(1,select,labels,symptoms,environment,
	xaxis,averagingwindow)
