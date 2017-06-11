import sys
sys.path.insert(0, '../3_extractFromDatabase')
import getDataDays as gd
import utilities as ut
import math
import numpy as np
import datetime
import pickle


### Time frame of the Analysis

outputfile='localData.txt'
start = '2016/01/05 00:00'
end = '2016/12/30 23:59'

info=ut.getDbStartEnd(start,end)


### Time conversion functions

def toDayNumber(unixtime):
	return math.floor(unixtime/86400)

localBeginningOfTime=toDayNumber(ut.toLinuxTime(start,'%Y/%m/%d %H:%M'))
localEndOfTime=toDayNumber(ut.toLinuxTime(end,'%Y/%m/%d %H:%M'))
nbTime=localEndOfTime-localBeginningOfTime+1

def toLocalDayNumber(unixtime):
	return (toDayNumber(unixtime)-localBeginningOfTime)

def convertDataToLocalDayNumber(data):
	for idx,val in enumerate(data['unixtime']):
		data['unixtime'][idx]=toLocalDayNumber(val)

def toDayDatetime(s):
    ye = int(datetime.datetime.fromtimestamp(s).strftime('%Y'))
    mo = int(datetime.datetime.fromtimestamp(s).strftime('%m'))
    da = int(datetime.datetime.fromtimestamp(s).strftime('%d'))
    t = datetime.datetime(ye, mo, da)
    return t


### For SQL calls regrouping values

def keepMax(data,maxtofind):
	datetime=data['datetime']
	val=data[maxtofind]
	n=len(datetime)-1
	toRemove=[]
	for idx, p in enumerate(datetime):
		if (idx!=n):
			if (datetime[idx]==datetime[idx+1]):
				if (val[idx]>val[idx+1]):
					toRemove.append(idx+1)
				else:
					toRemove.append(idx)
	m=len(toRemove)
	for i in range(1,m+1):
		rem=toRemove[m-i]
		for j in data:
			del data[j][rem]


### Get Data via SQL functions

painByLocation = gd.painByLocation()
dataKnees=painByLocation.getData(info,'Knees')
locHead=['Forehead and Eyes','Eyes (or around them)','Forehead']
dataHead=painByLocation.getData(info,locHead)
keepMax(dataHead,'intensity')
dataHands=painByLocation.getData(info,'Hands And Fingers')

manicTimePerDay = gd.manicTimePerDay()
dataManicTime=manicTimePerDay.getData(info)

sportDurByAct = gd.sportDurByAct()
dataAlpiSkiDuration=sportDurByAct.getData(info,'Alpi Ski')
dataClimbingDuration=sportDurByAct.getData(info,'Climbing')
dataDownSkiDuration=sportDurByAct.getData(info,'Down Ski')
dataMtBikeDuration=sportDurByAct.getData(info,'Mt Bike')
dataRoadBikeDuration=sportDurByAct.getData(info,'Road Bike')
dataSwimmingDuration=sportDurByAct.getData(info,'Swimming')
dataViaFerrataDuration=sportDurByAct.getData(info,'Via Ferrata')
dataWalkDuration=sportDurByAct.getData(info,'Walk')

whatPulsePerDay = gd.whatPulsePerDay()
dataWhatPulse=whatPulsePerDay.getData(info)

basisPerDay = gd.basisPerDay()
dataBasis=basisPerDay.getData(info)

sportBasisByAct = gd.sportBasisByAct()
dataAlpiSkiBasis=sportBasisByAct.getData(info,'Alpi Ski')
dataClimbingBasis=sportBasisByAct.getData(info,'Climbing')
dataDownSkiBasis=sportBasisByAct.getData(info,'Down Ski')
dataMtBikeBasis=sportBasisByAct.getData(info,'Mt Bike')
dataRoadBikeBasis=sportBasisByAct.getData(info,'Road Bike')
dataSwimmingBasis=sportBasisByAct.getData(info,'Swimming')
dataViaFerrataBasis=sportBasisByAct.getData(info,'Via Ferrata')
dataWalkBasis=sportBasisByAct.getData(info,'Walk')

general = gd.general()
dataGeneral = general.getData(info)

generalAct = gd.generalAct()
dataGeneralAct = generalAct.getData(info)

painStats = gd.painStats()
dataPainStats=painStats.getData(info)

climbViaIntensity = gd.climbViaIntensity()
dataClimbViaIntensity=climbViaIntensity.getData(info)

### Convert unix time to local day number

convertDataToLocalDayNumber(dataKnees)
convertDataToLocalDayNumber(dataHead)
convertDataToLocalDayNumber(dataHands)

convertDataToLocalDayNumber(dataManicTime)
convertDataToLocalDayNumber(dataAlpiSkiDuration)
convertDataToLocalDayNumber(dataClimbingDuration)
convertDataToLocalDayNumber(dataDownSkiDuration)
convertDataToLocalDayNumber(dataMtBikeDuration)
convertDataToLocalDayNumber(dataRoadBikeDuration)
convertDataToLocalDayNumber(dataSwimmingDuration)
convertDataToLocalDayNumber(dataViaFerrataDuration)
convertDataToLocalDayNumber(dataWalkDuration)
convertDataToLocalDayNumber(dataWhatPulse)
convertDataToLocalDayNumber(dataBasis)
convertDataToLocalDayNumber(dataAlpiSkiBasis)
convertDataToLocalDayNumber(dataClimbingBasis)
convertDataToLocalDayNumber(dataDownSkiBasis)
convertDataToLocalDayNumber(dataMtBikeBasis)
convertDataToLocalDayNumber(dataRoadBikeBasis)
convertDataToLocalDayNumber(dataSwimmingBasis)
convertDataToLocalDayNumber(dataViaFerrataBasis)
convertDataToLocalDayNumber(dataWalkBasis)

convertDataToLocalDayNumber(dataGeneralAct)
convertDataToLocalDayNumber(dataGeneral)
convertDataToLocalDayNumber(dataPainStats)
convertDataToLocalDayNumber(dataClimbViaIntensity)

### Create Final Data

environment=np.zeros((nbTime,39))
symptoms=np.zeros((nbTime,5))

def getQuantification(val):
	if (val=="Very Low"):
		return 1;
	elif (val=="Low"):
		return 2;
	elif (val=="Medium Low"):
		return 3;
	elif (val=="Medium"):
		return 4;
	elif (val=="High"):
		return 5;
	elif (val=="Very High"):
		return 6;
	else:
		return 0;

def fillFinalData(fdata,data,toFill):
	for col in toFill:
		numcol=col[0]
		colname=col[1]
		for idx,val in enumerate(data['unixtime']):
			if (type(data[colname][idx])!=str):
				fdata[val,numcol]+=data[colname][idx]
			else:
				fdata[val,numcol]=getQuantification(data[colname][idx])

fillFinalData(environment,dataManicTime,[[0,'duration']])
fillFinalData(environment,dataAlpiSkiDuration,[[1,'duration']])
fillFinalData(environment,dataClimbingDuration,[[2,'duration']])
fillFinalData(environment,dataDownSkiDuration,[[3,'duration']])
fillFinalData(environment,dataMtBikeDuration,[[4,'duration']])
fillFinalData(environment,dataRoadBikeDuration,[[5,'duration']])
fillFinalData(environment,dataSwimmingDuration,[[6,'duration']])
fillFinalData(environment,dataViaFerrataDuration,[[7,'duration']])
fillFinalData(environment,dataWalkDuration,[[8,'duration']])
fillFinalData(environment,dataWhatPulse,[[9,'keys'],[10,'clicks']])
fillFinalData(environment,dataBasis,[[11,'calories'],[12,'steps']])
fillFinalData(environment,dataAlpiSkiBasis,[[13,'calories'],[14,'steps']])
fillFinalData(environment,dataClimbingBasis,[[15,'calories'],[16,'steps']])
fillFinalData(environment,dataDownSkiBasis,[[17,'calories'],[18,'steps']])
fillFinalData(environment,dataMtBikeBasis,[[19,'calories'],[20,'steps']])
fillFinalData(environment,dataRoadBikeBasis,[[21,'calories'],[22,'steps']])
fillFinalData(environment,dataSwimmingBasis,[[23,'calories'],[24,'steps']])
fillFinalData(environment,dataViaFerrataBasis,[[25,'calories'],[26,'steps']])
fillFinalData(environment,dataWalkBasis,[[27,'calories'],[28,'steps']])
fillFinalData(environment,dataGeneral,[[29,'stress'],[30,'mood'],[31,'socquant'],[32,'weight']])
fillFinalData(environment,dataGeneralAct,[[33,'paper'],[34,'ubuntu'],[35,'driving'],[36,'store'],[38,'ridingcar']])
fillFinalData(environment,dataClimbViaIntensity,[[37,'effortInt']])

fillFinalData(symptoms,dataKnees,[[0,'intensity']])
fillFinalData(symptoms,dataHead ,[[1,'intensity']])
fillFinalData(symptoms,dataHands,[[2,'intensity']])
fillFinalData(symptoms,dataPainStats,[[3,'meanIntensity'],[4,'maxIntensity']])

xaxis=[]
str=ut.toLinuxTime(start,'%Y/%m/%d %H:%M')
for idx in range(0,nbTime):
	xaxis.append(ut.toDatetime(str+(idx*86400)-43200))
	# xaxis.append(toDayDatetime(str+(idx*86400)))


# Adjust calories to duration

restingCalPerMinute=1.8
environment[:,13]=environment[:,13]-restingCalPerMinute*environment[:,1]/60
environment[:,15]=environment[:,15]-restingCalPerMinute*environment[:,2]/60
environment[:,17]=environment[:,17]-restingCalPerMinute*environment[:,3]/60
environment[:,19]=environment[:,19]-restingCalPerMinute*environment[:,4]/60
environment[:,21]=environment[:,21]-restingCalPerMinute*environment[:,5]/60
environment[:,23]=environment[:,23]-restingCalPerMinute*environment[:,6]/60
environment[:,25]=environment[:,25]-restingCalPerMinute*environment[:,7]/60
environment[:,27]=environment[:,27]-restingCalPerMinute*environment[:,8]/60

# Add riding car to driving time
environment[:,35]=environment[:,35]+0.75*environment[:,38]

# Remove Edges from final data

def removeRow(data,lin):
	data=np.delete(data,lin,axis=0)
	return data

symptoms   =removeRow(symptoms,    nbTime-1)
environment=removeRow(environment, nbTime-1)
xaxis      =removeRow(xaxis,       nbTime-1)

symptoms   =removeRow(symptoms,    nbTime-2)
environment=removeRow(environment, nbTime-2)
xaxis      =removeRow(xaxis,       nbTime-2)

symptoms   =removeRow(symptoms,    0)
environment=removeRow(environment, 0)
xaxis      =removeRow(xaxis,       0)

symptoms   =removeRow(symptoms,    0)
environment=removeRow(environment, 0)
xaxis      =removeRow(xaxis,       0)


# Save in File

output = open(outputfile, 'wb')
pickle.dump([symptoms,environment,xaxis], output)
output.close()
