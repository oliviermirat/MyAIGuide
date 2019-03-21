# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 11:53:04 2016

@author: Olivier
"""
import dataset
import time
import numpy as np
import createDataBase

class painTab:
    m=np.array([['year',1,'int',1],
                ['month',1,'int',1],
                ['day',1,'int',1],
                ['location',0,'varchar',0],
                ['side',0,'varchar',0],
                ['intensity',0,'int',0],
                ['comment',0,'varchar',0],
                ['starttime',0,'int',0],
                ['endtime',0,'int',0]])
    timeFormat=['%Y/%m/%d','0']
    timeShift=86400
    tableName='pain'

createDataBase.createTable(painTab)

db = dataset.connect('sqlite:///olidata.db')

tableName='pain'
cols='year, month, day, location, side, intensity, comment, starttime, endtime'
vals1='2015,11,26,"Knees","0",5,"0",1448492400.0,1448578800.0'
vals2='2016,11,26,"Knees","0",5,"0",1448492400.0,1448578800.0'
vals3='2017,11,26,"Knees","0",5,"0",1448492400.0,1448578800.0'
vals4='2018,11,26,"Knees","0",5,"0",1448492400.0,1448578800.0'
vals5='2019,11,26,"Knees","0",5,"0",1448492400.0,1448578800.0'

av=time.time()

if (0):
    db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals1+')')
    db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals2+')')
    db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals3+')')
    db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals4+')')
    db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals5+')')
else:
    db.query('INSERT OR IGNORE INTO '+tableName+'('+cols+') VALUES ('+vals1+')'+',('+vals2+')'+',('+vals3+')'+',('+vals4+')'+',('+vals5+')')
    
result = db.query('SELECT * FROM pain')
for row in result:
   print(row['year'],row['month'],row['day'],row['location'],
         row['intensity'],row['starttime'],row['endtime'])
         
print('sql: ',time.time()-av)