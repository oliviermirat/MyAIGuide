"""
Created on Mon May 30 2020

@author: evadatinez
"""

from MyAIGuide.data.complaintsData import complaintsData
import numpy as np
from pathlib import Path
import pandas as pd


fname = 'data/raw/ParticipantData/Participant8Anonymized'
# create empty (full of 0s) test dataframe
i = pd.date_range('2015-11-19', periods=1550, freq='1D')
sLength = len(i)
empty = pd.Series(np.zeros(sLength)).values
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
test_data = complaintsData(fname=fname, data=test_data)

# read csv directly to compare results
path = Path(fname + '/Participant8Observations.csv')
# read csv from path
df_csv = pd.read_csv(path)
# extract date from 'date' column
df_csv['date_only'] = pd.to_datetime(df_csv.date,
                                     format='%Y-%m-%d',
                                     errors='ignore').dt.normalize()
# filter to have only the values from the date range we are interested on
df_csv = df_csv[df_csv['date_only'].isin(i)]


def test_complaintsData():
    df = test_data
    cols = [
        ('Awesome day!', 'complaintsAwesomeDay'),
        ('Loneliness', 'complaintsLoneliness'),
        ('Poor sleep', 'complaintsPoorSleep'),
        ('Sadness', 'complaintsSadness'),
        ('Stress', 'complaintsStress'),
        ('Tired', 'complaintsTired'),
        ('Worried anxious', 'complaintsWorriedAnxious')
        ]

    # check sum of values in each column agrees
    for col_info in cols:
        name_value, col = col_info
        sum_df = sum(df[col])
        sum_df_csv = sum(df_csv[df_csv.name == name_value]['intensity'])
        assert sum_df == sum_df_csv

    # indexed by days
    assert df.index.dtype == 'datetime64[ns]'
