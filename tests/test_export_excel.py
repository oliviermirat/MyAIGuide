"""
Created on Sat June 06 2020

@author: evadatinez
"""

from MyAIGuide.data.export_excel import exportParticipantDataframeToExcel
from MyAIGuide.data.complaintsData import complaintsData
import numpy as np
import os.path
import pandas as pd
from pandas._testing import assert_frame_equal


# create empty test dataframe with NaN
i = pd.date_range('2015-11-19', periods=1550, freq='1D')
sLength = len(i)
empty = np.empty(sLength)
empty[:] = np.nan
d = {
    'complaintsAwesomeDay': empty,
    'complaintsLoneliness': empty,
    'complaintsPoorSleep': empty,
    'complaintsSadness': empty,
    'complaintsStress': empty,
    'complaintsTired': empty,
    'complaintsWorriedAnxious': empty,
    'anotherNonRelevantColumn': empty
}
test_data = pd.DataFrame(data=d, index=i)

# update it with complaints data
fname = './data/raw/ParticipantData/Participant8Anonymized'
test_data = complaintsData(fname=fname, data=test_data)

# call function to test
export_cols = ['complaintsSadness', 'anotherNonRelevantColumn']
start_date = '2019-11-27'
end_date = '2019-12-05'
excel_fname = 'data_export_test'
exported_data = exportParticipantDataframeToExcel(test_data, start_date,
                                                  end_date, export_cols,
                                                  fname=excel_fname)
# expected data
expected_data = test_data[export_cols].copy()
# filter to have only the values from the date range we are interested on
dateRange = pd.date_range(start=start_date, end=end_date, freq='D')
expected_data = expected_data[expected_data.index.isin(dateRange)]


def test_exported_data():
    # verify excel file was exported correctly
    file_path = excel_fname + '.xlsx'
    os.path.isfile(file_path)
    # compare test and expected dataframes
    assert_frame_equal(expected_data, test_data)
