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
db.query('UPDATE taplog SET insttime=ms/1000')

db.query('UPDATE taplog SET insttime=insttime-3600 WHERE id>210 AND id<237')

"db.query('UPDATE taplog SET insttime=ms/1000+timezoneoffset/1000')"
