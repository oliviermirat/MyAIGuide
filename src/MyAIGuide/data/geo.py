"""
Functions that allow us to work with geographical data.
"""
__author__ = 'Levi Borodenko'
__license__ = 'mit'

import requests
from typing import List, Tuple

# Google Maps Elevation api
ELEVATION_BASE_URL = r'https://maps.googleapis.com/maps/api/elevation/'


def coords_to_query_string(coords:List[Tuple[float, float]], api_key:str, num_samples: int = 3) -> str:
    """
    Converts a list of lat,lon tuples into the query format required
    by Google Maps Elevation API.

    Args:
        coords: List of (lat,lon) tuples.
        api_key: Api key for Google Elevation API
        num_samples: Number of samples including endpoints to consider.

    Returns:
        Query string.

    """
    prefix = "json?path=" if len(coords) > 1 else "json?locations="
    path_string = ""
    for lat, lon in coords:
        path_string += f"{str(lat)},{str(lon)}|"
    path_string = path_string[:-1]

    sample_string = f"&samples={str(num_samples)}" if len(coords) > 1 else ""
    key_string = f"&key={api_key}"

    return prefix + path_string + sample_string + key_string


def get_elevation(locations: List[Tuple[float, float]], api_key: str) -> List[float]:
    """
    Takes a list containing (lat,lon) tuples and returns their respective elevations as a list.
    It utilises the Google Maps Elevation API.

    Note:
        RUNNING THIS FUNCTIONS COSTS MONEY. ~5$ per 2500 invocations.

    Args:
        locations: List of (lat,lon) tuples.
        api_key: Api key for Google Elevation API

    Returns:
        List of respective elevations in meters.

    """

    # get query string and final request url
    query_string = coords_to_query_string(locations, api_key)
    url = ELEVATION_BASE_URL + query_string

    # make request
    for _ in range(10):
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()["results"]
            elevations = []
            for result in results:
                elevations.append(result['elevation'])
            return elevations
    raise TimeoutError('ElevationAPI timed out!')


def get_cum_elevation_gain(elevations: List[float]) -> float:
    """
    Function that given the ordered sequence of elevation measurements during an
    activity, returns the total elevation gain.
    :param elevations: List of elevation measurements.
    :return: Cumulative elevation gain.
    """

    gain = 0
    last_elevation = elevations[0]
    del elevations[0]

    for elevation in elevations:

        # signed increase within the last change
        delta = elevation - last_elevation

        # only add uphill change
        gain += max(delta, 0)

        # update last_elevation to current elevation
        last_elevation = elevation

    return gain
