# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import defineTables as tabDef
import dataset
import csvToDatabase

csvFile='../1_initialRawData/manualLogPain.csv'

csvToDatabase.csvToDatabase(csvFile,tabDef.painTab)

db = dataset.connect('sqlite:///olidata.db')

#result = db.query('SELECT * FROM pain')
#for row in result:
#   print(row)
#
#result = db.query('SELECT * FROM pain')
#for row in result:
#   print(row['year'],row['month'],row['day'],row['location'],
#         row['intensity'],row['starttime'],row['endtime'])
