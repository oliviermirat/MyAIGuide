# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import defineTables as tabDef
import dataset
import csvToDatabase

csvFile='../1_initialRawData/taplog.csv'

csvToDatabase.csvToDatabase(csvFile,tabDef.taplogTab)

db = dataset.connect('sqlite:///olidata.db')

db.query('UPDATE taplog SET insttime=(ms/1000)')
# Not entirely sure why the following is necessary
db.query('UPDATE taplog SET insttime=insttime-32400 WHERE id>=501')
