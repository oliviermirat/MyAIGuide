import glob
import os
import pandas as pd
from pathlib import Path


def retrieve_moves_participant2(summary=False):
    """ Function creates a Dataframe of Moves data for Participant 2
        concatenates all csv files in a pandas DataFrame
    """
    path = Path('../data/raw/ParticipantData/Participant2Anonymized/MovesAppData/daily')

    if(not summary):
        folder_name = 'activities'
    else:
        folder_name = 'summary'

    all_files = glob.glob(os.path.join(path, folder_name, "*.csv"))
    df = pd.concat((pd.read_csv(f) for f in all_files))

    return df
