# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import defineTables as tabDef
import dataset
import csvToDatabase
import time
import datetime

# New and weird: this timeShift (60*60*9), California Time maybe ???
timeShift=32400

def toLinuxTime2(s,formatTime):
    t=time.mktime(datetime.datetime.strptime(s,formatTime).timetuple())
    return t

csvFile='../1_initialRawData/manualLogPhysicalActivities.csv'

csvToDatabase.csvToDatabase(csvFile,tabDef.sportTab)


db = dataset.connect('sqlite:///olidata.db')

result = db.query("SELECT id,year,month,day,start,duration FROM sports WHERE start!='taplog'")
for row in result:
    strr=str(row['year'])+'/'+str(row['month'])+'/'+str(row['day'])+'/'+str(row['start'])
    strr=toLinuxTime2(strr,'%Y/%m/%d/%H:%M')
    strend=strr+float(row['duration'])*60
    db.query('UPDATE sports SET starttime='+str(strr)+',endtime='+str(strend)+' WHERE id='+str(row['id']))

lastid=0
lasttime=0
result = db.query("SELECT s.id,t.insttime FROM sports s INNER JOIN taplog t ON s.starttime<t.insttime AND s.starttime+24*60*60>t.insttime WHERE s.start='taplog' AND t.cat2='Sport Str'")
for row in result:
	if (row['id']>lastid):
		if (row['insttime']>lasttime):
			db.query('UPDATE sports SET starttime='+str(row['insttime']+timeShift)+' WHERE id='+str(row['id']))
			lastid=row['id']
			lasttime=row['insttime']

lastid=0
lasttime=0
result = db.query("SELECT s.id,t.insttime FROM sports s INNER JOIN taplog t ON s.endtime>t.insttime AND s.endtime-24*60*60<t.insttime WHERE s.start='taplog' AND t.cat2='Sport End'")
for row in result:
	if (row['id']>lastid):
		if (row['insttime']>lasttime):
			db.query('UPDATE sports SET endtime='+str(row['insttime']+timeShift)+' WHERE id='+str(row['id']))
			lastid=row['id']
			lasttime=row['insttime']
