# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 21:07:43 2016

@author: Olivier
"""

import csvToDatabase
import dataset
import defineTables as tabDef

csvFile = "../1_initialRawData/ManicTimeData.csv"

csvToDatabase.csvToDatabase(csvFile, tabDef.manicTimeTab)

db = dataset.connect("sqlite:///olidata.db")
