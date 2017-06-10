import pickle
import findOptimalShift as optShift
import numpy as np
import matplotlib.pyplot as plt

input = open('localData3.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

cond=environment[:,34]<0
environment[cond,34]=0

maxx=max(environment[:,37])
minn=min(i for i in environment[:,37] if i > 0)
minn-=1
environment[:,37]=environment[:,37]-minn
cond=environment[:,37]<0
environment[cond,37]=0

# maxVal=np.zeros((10,20,10))
# maxPos=np.zeros((10,20,10))
maxCur=[0,0,0,0,0,0]

for i in range(1,10):
	for j in range(0,19):
		for k in range(0,9):
			for l in range(0,9):
				select=[[9,1],[10,1],[34,(1000*i)/60],[37,1000*j],[19,50*k],[23,50*l]]
				[shift,maxx]=optShift.testCorrel(2,select,symptoms,environment,xaxis)
				# maxVal[i,j,k]=maxx
				# maxPos[i,j,k]=shift
				if ((maxCur[0]<maxx)&(shift<20)):
				# if (maxCur[0]<maxx):
					maxCur[0]=maxx
					maxCur[1]=i
					maxCur[2]=j
					maxCur[3]=k
					maxCur[4]=l
					maxCur[5]=shift
				# print("i: ",i," ,j: ",j," ,k: ",k," ,shift: ",shift," ,maxx: ",maxx)

print(maxCur)
i=maxCur[1]
j=maxCur[2]
k=maxCur[3]
l=maxCur[4]
select=[[9,1],[10,1],[34,(1000*i)/60],[37,1000*j],[19,50*k],[23,50*l]]
[shift,maxx]=optShift.testCorrel(2,select,symptoms,environment,xaxis,1)


i=4
j=2
k=3
l=3
# i=6
# j=1
# k=3
# l=3
select=[[9,1],[10,1],[34,(1000*i)/60],[37,1000*j],[19,50*k],[23,50*l]]
[shift,maxx]=optShift.testCorrel(2,select,symptoms,environment,xaxis,1)


# 9:nbkeys
# 10:nbclicks
# 34:ubuntu
# 37:effortIntClimbVia
# 19:mtbikecal
# 23:swimcal



# hands=symptoms[:,2]
# press=environment[:,9]+environment[:,10]
# sport=environment[:,19]+environment[:,23]
# climbViaMaxInt=environment[:,37]
# ubuntu=environment[:,34]/60

# cond=ubuntu<0
# ubuntu[cond]=0
# simuPlot([hands,press+ubuntu*1650*3,sport,climbViaMaxInt],
# 	['hands','press','othersport','climbViaMaxInt'],xaxis)