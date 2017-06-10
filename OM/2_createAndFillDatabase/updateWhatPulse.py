# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import defineTables as tabDef
import dataset
import csvToDatabase

for i in range(1,87) :
    csvFile='../1_initialRawData/whatPulse/whatpulse-input-history'+str(i)+'.csv'
    csvToDatabase.csvToDatabase(csvFile,tabDef.whatPulseTab)

db = dataset.connect('sqlite:///olidata.db')

#db = dataset.connect('sqlite:///olidata.db')
#result =db.query('SELECT * FROM whatPulse WHERE id IN (SELECT max(id) FROM'+
#                ' whatPulse GROUP BY date)')
#for row in result:
#   print(row)
