"""
Created on Sat Jun 13 2020

@author: evadatinez
"""

import numpy as np
import pandas as pd


def select_data_input(row, col):
    """This function applies the logic to select the data input
    for a given row of data

    Params:
        row: 1 row of data frame with at least col and col+'_filled' columns
        col:  column name to check

    """
    # if column value is NaN then use the manually filled data
    if np.isnan(row[col]):
        return row[col + '_filled']
    # else keep the original data
    else:
        return row[col]


def manualDataImport(fname, data):

    """This function updates a dataframe with the manual data
    input from the participants when the tracked data was missing

    Params:
        fname: path to FILE with the manual data input
        data:  pandas dataframe to store data

    """

    # read imported data from excel
    import_data = pd.read_excel(fname, index_col=0)

    df = import_data.join(data, lsuffix='_filled', how='right')

    # we iterate over the columns of the imported data
    import_cols = list(import_data.columns)
    for icol in import_cols:
        # manually filled column has same col name + _manualFill suffix
        mcol = icol + '_manualFill'
        # iterate over rows of dataframe to apply selection of data input
        df[mcol] = df.apply(lambda row: select_data_input(row, icol),
                            axis=1)

    # drop columns ending with '_filled' as they were auxiliary columns
    df.drop([col for col in df.columns if '_filled' in col],
            axis=1, inplace=True)

    return df
