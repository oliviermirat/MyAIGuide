# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 16:25:09 2016

@author: Olivier
"""

shift=32000

import dataset

import createTables
import updateManicTime
import updatePain
import updateTaplog
import updateSport
import updateWhatPulse
import updateBasis

# import updateGeneral
import updateGeneralActivities

db = dataset.connect('sqlite:///olidata.db')
db.query("UPDATE basis SET date='2016-04-21 17:34Z', insttime=1461251388+"+str(shift)+", calories=250, steps=60 WHERE date='2016-04-21 22:00Z'")
db.query("UPDATE basis SET calories=2000, steps=3000 WHERE date='2016-04-21 22:01Z'")

db.query("UPDATE basis SET calories=270, steps=2500 WHERE insttime=1472029560+9*60*60")
