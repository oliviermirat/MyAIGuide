"""
Created on Mon June 02 2020

@author: evadatinez
"""
from datetime import datetime
from math import isnan
import pandas as pd
import xlsxwriter


def get_col_widths(df):
    """This function calculates the column width for index and all columns
        left to right

    Params:
        df:  pandas dataframe

    """
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in df.index.values] +
                  [len(str(df.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and
    # its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in df[col].values] +
                            [len(col)]) for col in df.columns]


def exportParticipantDataframeToExcel(data, start_date, end_date, export_cols,
                                      fname='data_export'):

    """This function writes the data of the export_cols in the desired
        timeframe into a formatted excel file

    Params:
        data:  pandas dataframe with the participant's data
        start_date: string of start date of data export
        end_date: string end date of data export
        export_cols: list of columns to export
        fname = string with desired file name

    """

    # filter data and select columns to export
    data2export = data[export_cols].copy()

    # filter to have only the values from the date range we are interested on
    dateRange = pd.date_range(start=start_date, end=end_date, freq='D')
    data2export = data2export[data2export.index.isin(dateRange)]

    # Create an XlsxWriter workbook and worksheet objects.
    workbook = xlsxwriter.Workbook(fname + '.xlsx')
    worksheet = workbook.add_worksheet()

    # Add a format. Bold text.
    bold_format = workbook.add_format({'bold': True, 'fg_color': '#FFC7CE'})

    # Add a header format.
    header_format = workbook.add_format({
        'bold': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1})

    # Add a date  format.
    date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})

    # Write the column headers with the defined format.
    col_names = ['date'] + export_cols
    for col_num, value in enumerate(col_names):
        worksheet.write(0, col_num, value, header_format)
    nrows, ncols = data2export.shape
    for i in range(0, nrows):
        for j in range(0, ncols):
            if not isnan(data2export.iloc[i][j]):
                worksheet.write(i + 1, j + 1,
                                data2export.iloc[i][j], bold_format)

    # Write the column headers with the defined format.
    for idx_num, value in enumerate(data2export.index.values):
        trans_value = datetime.strptime(str(value)[:10], '%Y-%m-%d')
        worksheet.write_datetime(idx_num + 1, 0, trans_value, date_format)

    # Set column width
    col_widths = get_col_widths(data2export)
    col_widths[0] = 10
    for i, width in enumerate(col_widths):
        worksheet.set_column(i, i, width)

    # Close the Excel workbook and output the Excel file.
    workbook.close()
