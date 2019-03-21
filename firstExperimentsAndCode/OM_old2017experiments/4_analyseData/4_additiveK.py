import pickle
import additiveModel as addMod

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

averagingwindow=7
coeff=0.6

select=[[12,1],[19,coeff]]
labels=['Knees','Steps','Mnt Bike']

addMod.additiveModel(0,select,labels,symptoms,environment,
	xaxis,averagingwindow)
