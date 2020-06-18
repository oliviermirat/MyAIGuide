from MyAIGuide.data.geo import get_elevation

# Oxford coord
LAT, LON = 51.752022, -1.257726


def get_elevation():
    elevation = get_elevation([(LAT, LON), (LAT, LON)], "API_KEY_HERE")
    expected_elevation = 69

    assert abs(elevation[0] - expected_elevation) < 3
    assert abs(elevation[1] - expected_elevation) < 3
