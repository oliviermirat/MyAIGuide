from MyAIGuide.data.geo import get_elevation, coords_to_query_string

# Oxford coord
LAT, LON = 51.752022, -1.257726


def test_get_elevation():
    elevation = get_elevation([(LAT, LON), (LAT, LON)])
    expected_elevation = 69

    assert abs(elevation[0] - expected_elevation) < 3
    assert abs(elevation[1] - expected_elevation) < 3


def test_coords_to_query_string():
    result = coords_to_query_string([(LAT, LON), (LON, LAT)])
    assert result == "51.752022,-1.257726|-1.257726,51.752022"
