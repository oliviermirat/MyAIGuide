"""
Functions that allow us to work with geographical data.
"""
__author__ = 'Levi Borodenko'
__license__ = 'mit'

import requests
from typing import List, Tuple

# OpenStreetMaps elevation api
ELEVATION_BASE_URL = r'https://api.open-elevation.com/api/v1/lookup?locations='


def coords_to_query_string(coords:List[Tuple[float, float]]) -> str:
    """
    Converts a list of lat,lon tuples into the query format required
    by https://open-elevation.com/.

    Args:
        coords: List of lat,lon tuples.

    Returns:
        Query string.

    """
    result = ""
    for lat, lon in coords:
        result += str(lat) + "," + str(lon) + "|"
    return result[:-1]


def get_elevation(locations: List[Tuple[float, float]]) -> List[float]:
    """
    Takes a list containing (lat,lon) tuples and returns their respective elevations as a list.
    It utilises the public API at https://open-elevation.com/ which is VERY SLOW and UNSTABLE.

    Note:
        This API is HORRENDOUSLY slow. So it is important to treasure its outputs!

    Args:
        locations: List of lat,lon tuples.

    Returns:
        List of respective elevations.

    """

    # get query string and final request url
    query_string = coords_to_query_string(locations)
    url = ELEVATION_BASE_URL + query_string
    print(query_string)

    # make request
    for _ in range(10):
        print(f"Trying to request elevations from public API. Try {_+1}/10")
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()["results"]
            elevations = []
            for result in results:
                elevations.append(result['elevation'])
            print("Successfully retrieved elevations.")
            return elevations
    raise TimeoutError('OpenElevationAPI timed out!')