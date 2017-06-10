import pickle
import numpy as np
import matplotlib.pyplot as plt
import moysAndGroups as mam

def chooseAndPlot(groups,cols):
	for idx, g in enumerate(groups):
		plt.plot(g[:,cols[0]], g[:,cols[1]], '.', label=str(idx))
		leg=plt.legend(loc='upper center', shadow=True)
		if leg:
			leg.draggable()
	plt.show()

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

head=symptoms[:,1]
manictime=environment[:,0]/(60*60)
paper=environment[:,33]/60
ubuntu=environment[:,34]/60
cond=ubuntu<0
ubuntu[cond]=0

papUbuMan=paper+ubuntu+manictime

# Analysis

if (0):
	groupK=mam.defineGroup(papUbuMan,head,[2.9,3.5,3.9])
	past=mam.createPastMoy(papUbuMan,[1,1,1],[-3,-2,-1])
	groupK2=mam.defineGroup(past,head,[2.9,3.5,3.9])

	pastSymp=mam.createPastMoy(head,[1],[-1])
	groupK3=mam.defineGroup(pastSymp,head,[2.9,3.5,3.9])


	print([np.mean(groupK[0]),np.mean(groupK[1]),np.mean(groupK[2]),np.mean(groupK[3])])
	print([np.mean(groupK2[0]),np.mean(groupK2[1]),np.mean(groupK2[2]),np.mean(groupK2[3])])
	print([np.mean(groupK3[0]),np.mean(groupK3[1]),np.mean(groupK3[2]),np.mean(groupK3[3])])
	plt.plot(groupK3[0],groupK2[0],'.',label='0')
	plt.plot(groupK3[1],groupK2[1],'.',label='1')
	plt.plot(groupK3[2],groupK2[2],'.',label='2')
	plt.plot(groupK3[3],groupK2[3],'.',label='3')
	leg=plt.legend(loc='upper center', fontsize=9)
	if leg:
		leg.draggable()
	plt.show()


if (1):
	past=mam.createPastMoy(papUbuMan,[1,1,1],[-3,-2,-1])
	# pastHead2=createPastMoy(head,[1,1,1],[-1,-2,-3])
	pastHead2=mam.createPastMoy(head,[1],[-1])
	groupM=mam.defineGroupMult(past,pastHead2.transpose(),head,[2.9,3.5,3.9])
	# groupM=defineGroupMult(papUbuMan,head,head,[2.9,3.5,3.9])
	for i in range(0,4):
		print("")
		for j in range(0,4):
			if (len(groupM[i][j])>0):
				print(i, j, len(groupM[i][j]), np.mean(groupM[i][j]) )
			else:
				print(i, j, len(groupM[i][j]), -1 )

