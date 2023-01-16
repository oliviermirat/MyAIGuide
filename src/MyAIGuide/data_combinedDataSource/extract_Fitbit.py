import numpy as np
import pandas as pd
import os
import json
import datetime as dt
import pdb

############################

def extract_fitbit(path, file_prefix):
    """
    This function extract info from many .json files (sorted by date) and 
     return them into a pandas DataFrame

    Parameters
    ----------
    path : String. Address of the directory where the files are
    
    file_prefix : String. Since there are many files to read, and they have all
    the same prefix, one must provide it

    Returns
    -------
    A pandas dataframe

    """

    df = pd.DataFrame()

    for file_name in os.listdir(path):
        if file_name.startswith(file_prefix + '-'):
            with open(path + file_name) as data_file:    
                data = json.load(data_file)
            df_ = pd.json_normalize(data,errors='ignore')
            df = pd.concat([df,df_], axis=0, ignore_index=True)

    # Since the Google timeline is reported as UCT, we
    #assume here that the fitbit time is alike
    df['dateTime'] = pd.to_datetime(df['dateTime'], utc=True)

    return df
