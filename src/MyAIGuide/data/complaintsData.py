"""
Created on Mon May 30 2020

@author: evadatinez
"""

from pathlib import Path
import pandas as pd


def complaintsData(fname, data):

    """This function updates a dataframe with the CSV data
    with complaints

    Params:
        fname: path to FILE
        data:  pandas dataframe to store data

    """

    path = Path(fname + '/Participant8Observations.csv')

    # read csv from path
    df = pd.read_csv(path)

    # extract date from 'date' column
    df['date_only'] = pd.to_datetime(df.date,
                                     format='%Y-%m-%d',
                                     errors='ignore').dt.normalize()

    # pivot dataframe (long -> wide) to have one row per date
    pdf = df.pivot(index='date_only', columns='name', values='intensity')

    # rename the columns to match the data
    pdf.rename(columns={
        'Awesome day!': 'complaintsAwesomeDay',
        'Loneliness': 'complaintsLoneliness',
        'Poor sleep': 'complaintsPoorSleep',
        'Sadness': 'complaintsSadness',
        'Stress': 'complaintsStress',
        'Tired': 'complaintsTired',
        'Worried anxious': 'complaintsWorriedAnxious'
        }, inplace=True)

    # update data with the pivoted dataframe
    data.update(pdf)

    return data
