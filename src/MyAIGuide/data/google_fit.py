"""
Interface to Google Fit data.
"""
__author__ = 'Levi Borodenko'
__license__ = 'mit'

from pathlib import Path
from typing import Union, List
from functools import cached_property
import pandas as pd
import json

DATA_DIR = Path('../data/raw/ParticipantData')


class GoogleFitData(object):
    """Class providing a link to the Google Fit json files.

    Args:
        path_to_json (:obj:`Path`, `str`): Path to json data dump.
    """
    def __init__(self, path_to_json: Union[Path, str]):
        self.path = Path(path_to_json)
        if not self.path.exists():
            raise FileNotFoundError(f'Provided path {self.path} does not exist.')
        elif self.path.suffix != '.json':
            raise ValueError('Provided path should lead to a .json file.')

    @cached_property
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

    @cached_property
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
        df = df.set_index('start_time')
        df = df.resample('D').sum()
        df = df.rename(columns={'start_time': 'day'})

        return df



