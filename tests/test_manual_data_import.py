"""
Created on Tue June 16 2020

@author: evadatinez
"""

from MyAIGuide.data.manualDataImport import select_data_input, manualDataImport
from MyAIGuide.data.complaintsData import complaintsData
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal


def test_select_data_input():
    d_test = {
        'A': [np.nan, np.nan, 1.0, 3.0],
        'A_filled': [0.0, np.nan, np.nan, 2.0]
    }

    test_data = pd.DataFrame(data=d_test)

    icol = 'A'
    mcol = icol + '_manualFill'
    test_data[mcol] = test_data.apply(lambda row: select_data_input(row, icol),
                                      axis=1)
    d_expected = {
        'A': [np.nan, np.nan, 1.0, 3.0],
        'A_filled': [0.0, np.nan, np.nan, 2.0],
        'A_manualFill': [0.0, np.nan, 1.0, 3.0]
    }
    expected_data = pd.DataFrame(data=d_expected)

    assert_frame_equal(expected_data, test_data)


def test_manualDataImport():
    # create empty test dataframe with NaN
    start_date = '2019-11-26'
    end_date = '2019-12-01'
    i = pd.date_range(start=start_date, end=end_date, freq='D')
    sLength = len(i)
    empty = np.empty(sLength)
    empty[:] = np.nan
    d = {
        'complaintsAwesomeDay': empty,
        'complaintsSadness': empty,
        'anotherNonRelevantColumn': empty
    }
    data = pd.DataFrame(data=d, index=i)

    # update it with complaints data
    fname_participant = '../data/raw/ParticipantData/Participant8Anonymized'
    data = complaintsData(fname=fname_participant, data=data)

    # import excel test data.
    # - value in cell B2 was overwritten tot est we keep original value.
    # - first value in 'anotherNonRelevantColumn_manualFill' should be a NaN
    #   to test we are not modifying values out of the
    #   date range in the excel file.
    fname_test_data = '../data/raw/excelFilesForMissingDataFill/test_manual_fill_data.xlsx'

    test_data = manualDataImport(fname_test_data, data)
    d_expected = {
        'complaintsAwesomeDay': empty,
        'complaintsSadness': [0.0, 1.0, np.nan, np.nan, 1.0, 1.0],
        'anotherNonRelevantColumn': empty,
        'complaintsSadness_manualFill': [0.0, 1.0, 23.0, 24.0, 1.0, 1.0],
        'anotherNonRelevantColumn_manualFill': [np.nan, 12.0, 13.0, 14.0, 15.0, 16.0]
    }

    expected_data = pd.DataFrame(data=d_expected, index=i)

    assert_frame_equal(expected_data, test_data)
