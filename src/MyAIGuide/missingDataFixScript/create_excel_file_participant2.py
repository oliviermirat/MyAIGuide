#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 21:09:12 2020

@author: anniewong
"""

import pickle
import sys
sys.path.insert(1, '../src/MyAIGuide/data')

from data.export_excel import exportParticipantDataframeToExcel

# Read datafile participant 2
input = open("../data/preprocessed/preprocessedDataParticipant2.txt", "rb")
data = pickle.load(input)
input.close()


# Generate excel file based on data

# export_cols = data.columns.tolist()

# Only export kneepain column
export_cols=['kneepain']
start_date=data.index[0]
end_date=data.index[-1]
excel_fname='missing_values_participant2'

# export excel 

exported_data = exportParticipantDataframeToExcel(data, start_date,
                                                  end_date, export_cols,
                                                  fname=excel_fname)

