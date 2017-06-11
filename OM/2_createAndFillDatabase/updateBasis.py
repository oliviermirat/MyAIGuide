# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import defineTables as tabDef
import dataset
import csvToDatabase

csvFile='../1_initialRawData/bodymetrics.csv'

csvToDatabase.csvToDatabase(csvFile,tabDef.basisTab)

# View the taplog file to know what to change below (this is time zone stuff)
db = dataset.connect('sqlite:///olidata.db')
db.query('UPDATE basis SET insttime=insttime+3600 WHERE id<133318')
db.query('UPDATE basis SET insttime=insttime+7200 WHERE (id>133318 AND id<=359920)')
db.query('UPDATE basis SET insttime=insttime-21600 WHERE (id>=359921 AND id<=361360)')
db.query('UPDATE basis SET insttime=insttime-25200 WHERE (id>=361361 AND id<451567)')
db.query('UPDATE basis SET insttime=insttime-28800 WHERE id>=451568')

# Sometimes, basis lost some data or there were some other technical
# issues => needs to be fixed manualLogPhysicalActivities

# TO DO !!!
