import pickle
import additiveModelSuperposition as addMod
import numpy as np

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

averagingwindow=20
averagingwindow2=4
averagingwindowBig=60

# coeff=1 #0.6
# select=[[12,1],[19,coeff],[25,0.5],[27,0.5]]
# labels=['Knees','Steps','Mnt Bike','viacal','walkcal']

coeff=0.6
select=[[12,1],[19,coeff]]
labels=['Knee Symptom','Steps Taken','Mnt Bike Cal']
# for i in range(0,len(environment[:,40])):
	# if (environment[i,40]>100000):
		# environment[i,40]=environment[i-1,40]
		# print("RESCALED pondSteps one time")
# for i in range(0,len(environment[:,40])):
	# environment[i,40]=np.exp(0.0001*environment[i,40])
		
		
# select=[[28,1]]#,[16,1]]
# labels=['Knees','Walk Dur']#,'Climb Dur']

for i in range(3,len(environment[:,11])):
	cal = environment[i,11]
	if cal < 1700:
		environment[i,11] = np.mean(environment[i-3:i,11])
		environment[i,12] = np.mean(environment[i-3:i,12])

addMod.additiveModel(0,select,labels,symptoms,environment,
	xaxis,averagingwindow,averagingwindow2,averagingwindowBig,3.6)
