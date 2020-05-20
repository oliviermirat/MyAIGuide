# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 18:21:35 2016

@author: Olivier
"""

import createDataBase
import defineTables as tabDef

createDataBase.createTable(tabDef.basisTab)
createDataBase.createTable(tabDef.painTab)
createDataBase.createTable(tabDef.sportTab)
createDataBase.createTable(tabDef.manicTimeTab)
createDataBase.createTable(tabDef.screenSaverTab)
createDataBase.createTable(tabDef.whatPulseTab)
createDataBase.createTable(tabDef.taplogTab)

createDataBase.createTable(tabDef.general)
createDataBase.createTable(tabDef.generalActivities)
