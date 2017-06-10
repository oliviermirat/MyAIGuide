import numpy as np

# Moys

def createPastMoy(data,weigths,weightsPos):
	nbWeights=len(weigths)
	n=len(data)
	if (type(data[0])==np.ndarray):
		m=len(data[0])
	else:
		m=1
	past=np.zeros((n,m))
	for i in range(0,n):
		sumw=0
		for j in range(0,nbWeights):
			relaPos=weightsPos[j]
			curWeight=weigths[j]
			if ((i+relaPos>=0)&(i+relaPos<n)):
				past[i,:]+=data[i+relaPos]*curWeight
				sumw+=curWeight
		if (sumw):
			past[i,:]=past[i,:]/sumw
	return past


# Groups

def extract(cond,nEnv,envi):
	cond=np.array([cond,]*nEnv).transpose()
	out=np.extract(cond,envi)
	out=out.reshape((int(len(out)/nEnv), nEnv))
	return out

def defineGroup(envi,symp,thres):
	groups=[]
	n=len(thres)
	# nEnv=len(envi[0])
	nEnv=1

	cond=symp<=thres[0]
	groups.append(extract(cond,nEnv,envi))

	for i in range(1,n):
		cond=(symp>thres[i-1])&(symp<=thres[i])
		groups.append(extract(cond,nEnv,envi))
	
	cond=symp>thres[n-1]
	groups.append(extract(cond,nEnv,envi))
	
	return groups

def getLabels(symp,thres):
	n=len(symp)
	cond=symp>thres
	labels=np.zeros((n,1))
	labels[cond]=1
	return labels

def findcond(i,n,thres,symp):
	if (i==0):
		thresmin=0
	else:
		thresmin=thres[i-1]
	if (i==n):
		thresmax=10
	else:
		thresmax=thres[i]
	cond=((symp>thresmin)&(symp<=thresmax))
	return cond

def defineGroupMult(envi,symp,symp2,thres):

	n=len(thres)
	groups=np.zeros((n+1,n+1))
	nEnv=1
	# groups=[[0]*(n+1)]*(n+1)
	groups={}
	# nEnv=len(envi[0])

	for i in range(0,n+1):
		groups[i]={}
		for j in range(0,n+1):
			cond1=findcond(i,n,thres,symp)
			cond2=findcond(j,n,thres,symp2)
			cond=(cond1&cond2)
			groups[i][j]=extract(cond,nEnv,envi)
	
	return groups