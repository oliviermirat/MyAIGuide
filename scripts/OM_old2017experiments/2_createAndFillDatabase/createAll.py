# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 16:25:09 2016

@author: Olivier
"""

import createTables
import dataset
import updateBasis

# import updateGeneral
import updateGeneralActivities
import updateManicTime
import updatePain
import updateScreenSaver
import updateSport
import updateTaplog
import updateWhatPulse

db = dataset.connect("sqlite:///olidata.db")
