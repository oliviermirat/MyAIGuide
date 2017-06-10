from sklearn import svm
import pickle
import numpy as np
import moysAndGroups as mam

def testSVM(trainingPredictors,trainingExpected,testPredictors,testExpected):
	clf = svm.SVC()
	clf.fit(trainingPredictors,trainingExpected)
	res=clf.predict(testPredictors)
	t=res==testExpected
	# print(t)
	return sum(t)

def testMethod(predictors,expected):
	n=len(expected)
	restot=0
	restotPos=0
	restotNeg=0
	for i in range(0,n):
		trainingPredictors=predictors[:]
		del trainingPredictors[i]
		trainingExpected=expected[:]
		del trainingExpected[i]
		testPredictors=[predictors[i]]
		testExpected=[expected[i]]
		res=testSVM(trainingPredictors,trainingExpected,testPredictors,testExpected)
		restot+=res
		if (expected[i]):
			restotPos+=res
		else:
			restotNeg+=res
		# print(i,"valid: ",res," ; reality: ",expected[i])

	# print(restot,n,restot/n)
	# print(restotPos,sum(np.array(expected)==1),restotPos/sum(np.array(expected)==1))
	# print(restotNeg,sum(np.array(expected)==0),restotNeg/sum(np.array(expected)==0))
	print(restot/n,restotPos/sum(np.array(expected)==1),
		restotNeg/sum(np.array(expected)==0))

def createDataSet(symptoms,environment):
	head=symptoms[:,1]
	past=mam.createPastMoy(environment,[0.1,0.2,0.5,1],[-3,-2,-1,0])
	# past=past[:,[0,33,34,35]]
	labels=mam.getLabels(head,3.5)
	return [past,labels]

def structChanges(predictors,expected):
	predictors=predictors.tolist()
	expected=expected.transpose().tolist()
	expected=expected[0]
	return [predictors,expected]


# Actual Test

input = open('localData.txt', 'rb')
localData = pickle.load(input)
input.close()
symptoms=localData[0]
environment=localData[1]
xaxis=localData[2]

[predictors,expected]=createDataSet(symptoms,environment)

[predictors,expected]=structChanges(predictors,expected)

testMethod(predictors,expected)
