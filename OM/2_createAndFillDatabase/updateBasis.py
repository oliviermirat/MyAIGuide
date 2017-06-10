# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import defineTables as tabDef
import dataset
import csvToDatabase

#csvFile='../../QS/basis/bodymetrics_2012-01-30T00_00_00_2016-01-31T20_14_00.csv'
csvFile='../1_initialRawData/bodymetrics.csv'

csvToDatabase.csvToDatabase(csvFile,tabDef.basisTab)

db = dataset.connect('sqlite:///olidata.db')
db.query('UPDATE basis SET insttime=insttime+3600 WHERE id<133318')
db.query('UPDATE basis SET insttime=insttime+2*3600 WHERE id>133318')
