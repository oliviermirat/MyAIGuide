"""
Interface to Google Fit data.
"""
__author__ = 'Levi Borodenko'
__license__ = 'mit'

from pathlib import Path
from typing import Union

DATA_DIR = Path('./data/raw/ParticipantData')


class GoogleFitData(object):
    def __init__(self, path_to_json: Union[Path, str]):
        self.path = Path(path_to_json)
        if not self.path.exists():
            raise FileNotFoundError(f'Provided path {self.path} does not exist.')
        elif self.path.suffix != '.json':
            raise ValueError('Provided path should lead to a .json file.')



