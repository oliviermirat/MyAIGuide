# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 09:49:48 2016

@author: Olivier
"""

import sys
sys.path.insert(0, '../extractFromDatabase')

import getDataDays as gd
import utilities as ut
import matplotlib.pyplot as plt

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

def plotExpected(data,y,num=111,show=1):
	plt.subplot(num)
	plt.plot(data["datetime"], data[y])
	if (show):
		plt.show()
    
def plotBarExpected(data,y,num=111,show=1):
    ax = plt.subplot(num)
    ax.bar(data["datetime"], data[y], width=1)
    ax.xaxis_date()
    if (show):
    	plt.show()


start = '2016/02/01 00:00'
end = '2016/04/03 23:59'
info=ut.getDbStartEnd(start,end)


painByLocation = gd.painByLocation()
data1=painByLocation.getData(info,'Knees')

manicTimePerDay = gd.manicTimePerDay()
data2=manicTimePerDay.getData(info)

sportDurByAct = gd.sportDurByAct()
data3=sportDurByAct.getData(info,'Climbing')

whatPulsePerDay = gd.whatPulsePerDay()
data4=whatPulsePerDay.getData(info)

basisPerDay = gd.basisPerDay()
data5=basisPerDay.getData(info)

sportBasisByAct = gd.sportBasisByAct()
data6=sportBasisByAct.getData(info,'Climbing')



plotExpected(data1,"intensity")
plotExpected(data2,"duration")
plotBarExpected(data3,"duration")
plotExpected(data4,"clicks")
plotExpected(data5,"steps")
plotExpected(data5,"calories")
plotBarExpected(data6,"calories")
