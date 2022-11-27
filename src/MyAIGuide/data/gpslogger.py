"""
Handle GPSLogger files
"""
__author__ = 'Levi Borodenko'
__license__ = 'mit'

from pathlib import Path
from typing import Union
import pandas as pd
try:
  from calculateCumulatedElevationGainMoves import gpx_to_dataframe
except ModuleNotFoundError:
  from src.MyAIGuide.data.calculateCumulatedElevationGainMoves import gpx_to_dataframe
try:
  from geo import get_cum_elevation_gain
except ModuleNotFoundError:
  from src.MyAIGuide.data.geo import get_cum_elevation_gain


def get_df_from_file(file: Path) -> pd.DataFrame:
    """
    Parses the GPSLogger file into a df.
    Args:
        file: Path to .gpx file.

    Returns:
        dataframe containing dateTime and elevation_gain

    """

    gpx_df = gpx_to_dataframe(file)

    # set starting time as overall activity time.
    date_time = gpx_df.time[0]

    # get elevations
    elevations = [i for i in gpx_df.elevation]

    # calculate respective elevation gain
    elevation_gain = get_cum_elevation_gain(elevations)

    # return as dataframe
    df = pd.DataFrame(data={
        'elevation_gain': [elevation_gain]
    }, index=[date_time])
    return df


def collect_gpslogger_activities(path_to_dir: Union[Path, str]) -> pd.DataFrame:
    """
    Takes all GPSLogger .gpx file from the folder path_to_dir and processes them into a df.
    Args:
        path_to_dir: path to folder containing GPSLogger .gpx files.

    Returns:
        Dataframe with dateTime and elevation_gain columns.

    """

    directory = Path(path_to_dir)
    is_first = True

    # only consider .gpx files.
    for file in directory.iterdir():
        if file.suffix == ".gpx":

            # set-up df
            if is_first:
                df = get_df_from_file(file)
                is_first = False

            # append to set-up df.
            else:
                df = df.append(get_df_from_file(file))

    # resample to daily aggregated data
    df = df.resample("D").sum()

    # NOTE: strangly important to do this as having timezone info breaks
    # .update with the master df which has no timezone.
    df.index = df.index.astype("datetime64[ns]")
    return df


def get_gpslogger_activities(fname: Union[Path, str], data: pd.DataFrame) -> pd.DataFrame:
    """
    This function updates a dataframe with the data
    gathered from the GPSLogger gpx files contained in fname.

    It updates the "elevation_gain" column of the master df.

    Params:
        fname: path to data folder containing gpx data
        data:  pandas data frame to store data
    """

    # return the extracted dataframe
    new_data = collect_gpslogger_activities(fname)

    # update data
    data.update(new_data)

    return data
