from unittest import TestCase

from MyAIGuide.data.geo import get_elevation, get_cum_elevation_gain

# Oxford coord
LAT, LON = 51.752022, -1.257726
ELEVATIONS = [0, -5, 10, 5, 10, 10, -10, 10]
GAIN = 0 + 15 + 0 + 5 + 0 + 0 + 20


def get_elevation():
    elevation = get_elevation([(LAT, LON), (LAT, LON)], "API_KEY_HERE")
    expected_elevation = 69

    assert abs(elevation[0] - expected_elevation) < 3
    assert abs(elevation[1] - expected_elevation) < 3


def test_get_cum_elevation_gain():
    assert get_cum_elevation_gain(ELEVATIONS) == GAIN
