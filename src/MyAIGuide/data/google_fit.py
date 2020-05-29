"""
Interface to Google Fit data.
"""
__author__ = 'Levi Borodenko'
__license__ = 'mit'

from pathlib import Path
from typing import Union, List
import pandas as pd
import json

DATA_DIR = Path('./data/raw/ParticipantData')


class GoogleFitData(object):
    """Class providing a link to the Google Fit json files.

    Args:
        path_to_json (:obj:`Path`, `str`): Path to json data dump.

    Properties:
        - raw_json (dict): raw json extracted from the json file.
        - df (pd.Dataframe): Dataframe of steps per day.

    Methods:
        - _process_json: Converts raw json into an easy to use dict.
    """
    def __init__(self, path_to_json: Union[Path, str]):
        self.path = Path(path_to_json)
        if not self.path.exists():
            raise FileNotFoundError(f'Provided path {self.path} does not exist.')
        elif self.path.suffix != '.json':
            raise ValueError('Provided path should lead to a .json file.')

    @property
    def raw_json(self) -> dict:
        """Retrieves the object from the json file provided in path_to_json.

        Returns:
            Dictionary loaded from the json file.

        """
        with open(self.path, 'rb') as json_file:
            raw_json = json.load(json_file)
        return raw_json

    def _process_json(self) -> List[dict]:
        """Processes the json to get start_time, end_time and steps out of the json.

        Returns:
            List of dicts, each corresponding to a recorded time interval (day).

            ``[{start_time: ..., end_time: ..., steps: ...}, ...]``
        """

        raw_json = self.raw_json

        # raw json is wrapped in 'bucket'
        raw_json = raw_json['bucket']

        intervals = []
        for interval in raw_json:
            for sub_interval in interval['dataset']:
                for point in sub_interval['point']:

                    # grabbing finest grained step count
                    start_time = int(point['startTimeNanos'])
                    end_time = int(point['endTimeNanos'])
                    steps = int(point['value'][0]['intVal'])

                    information = dict(start_time=start_time,
                                       end_time=end_time,
                                       steps=steps)
                    intervals.append(information)

        return intervals

    @property
    def df(self) -> pd.DataFrame:
        """Converts the processed json to a `pd.DataFrame`.

        Returns:
            df (pd.Dataframe): A dataframe of daily steps indexed by a datetime
            representation of the day.

        """

        # load records
        records = self._process_json()
        df = pd.DataFrame.from_records(data=records)

        # convert time to pd.datetime
        df['end_time'] = pd.to_datetime(df['end_time'], unit="ns")
        df['start_time'] = pd.to_datetime(df['start_time'], unit="ns")

        # resample so that we have steps per day
        df = df.rename(columns={'start_time': 'dateTime', 'steps': 'googlefitSteps'})
        df = df.set_index('dateTime')
        df = df.resample('D').sum()

        return df


def get_google_fit_steps(fname: Union[Path, str], data: pd.DataFrame) -> pd.DataFrame:
    """
    This function updates a dataframe with the JSON data
    gathered from the GoogleFit API.
    It updates the values in the `googlefitSteps` column.

    Params:
        fname: path to data folder for participant X
        data:  pandas data frame to store data
    """

    directory = Path(fname)

    # find json file with GoogleFit data
    for child in directory.iterdir():
        if child.suffix == ".json" and "GoogleFit" in child.stem:
            path_to_json = child

    # initiate interface to file
    json_interface = GoogleFitData(path_to_json)

    # return the extracted dataframe
    new_data = json_interface.df

    # update data
    data.update(new_data)

    return data

