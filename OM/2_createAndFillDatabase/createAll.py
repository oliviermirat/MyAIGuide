# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 16:25:09 2016

@author: Olivier
"""

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
