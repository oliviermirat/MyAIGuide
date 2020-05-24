import glob
import os
import pandas as pd
from pathlib import Path


def retrieve_moves_participant2():
    """ Function creates a Dataframe of Moves data for Participant 2
        concatenates all csv files in a pandas DataFrame
    """
    path = Path('../data/raw/ParticipantData/Participant2Anonymized/MovesAppData/daily/summary')

    all_files = glob.glob(os.path.join(path, "*.csv"))
    df = pd.concat((pd.read_csv(f) for f in all_files))

    # TODO:
    # cleanup of df to look like https://github.com/oliviermirat/MyAIGuide/blob/master/scripts/1_createDataFrame.py

    return df
