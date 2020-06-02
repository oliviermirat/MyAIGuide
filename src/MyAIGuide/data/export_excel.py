"""
Created on Mon June 02 2020

@author: evadatinez
"""

import pandas as pd
# import xlsxwriter


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

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(fname + '.xlsx', engine='xlsxwriter',
                            datetime_format='yyyy-mm-dd')

    # Convert the dataframe to an XlsxWriter Excel object.
    data2export.to_excel(writer, sheet_name='Sheet1',
                         startrow=1, header=False)

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Add a format. Bold text.
    format_bold = workbook.add_format({'bold': True})

    # Add a header format.
    header_format = workbook.add_format({
        'bold': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1})

    # Write a conditional format over a range.
    worksheet.conditional_format('A1:Z6', {'type': 'no_blanks',
                                           'format': format_bold})

    col_names = [data2export.index.name] + export_cols
    # Write the column headers with the defined format.
    for col_num, value in enumerate(col_names):
        worksheet.write(0, col_num, value, header_format)

    # Set column width
    for i, width in enumerate(get_col_widths(data2export)):
        worksheet.set_column(i, i, width)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
