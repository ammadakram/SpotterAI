import pytest

from planner.domain.corridor import corridor_cells

# An east-west line along latitude 40° from -100° to -98° (two points, one long segment).
LINE = [(-100.0, 40.0), (-98.0, 40.0)]
MI_PER_DEG_LAT = 69.0


def test_cells_whose_centre_is_within_30_miles_of_the_line():
    # Rows 39.75 and 40.25 are ~17 mi away; 39.25 and 40.75 are ~52 mi away.
    # Past the ends, -100.25 / -97.75 are ~22 mi away; -100.75 / -97.25 are ~42 mi away.
    cells = corridor_cells([LINE])

    lons = [-100.25, -99.75, -99.25, -98.75, -98.25, -97.75]
    assert sorted(cells) == sorted((lon, lat) for lon in lons for lat in (39.75, 40.25))


@pytest.mark.parametrize(("distance_mi", "included"), [(25, True), (35, False)])
def test_corridor_is_30_miles_wide(distance_mi, included):
    # A line south of the 40.25 row, at the given distance from its centres.
    lat = 40.25 - distance_mi / MI_PER_DEG_LAT
    cells = corridor_cells([[(-99.5, lat), (-99.0, lat)]])

    assert ((-99.25, 40.25) in cells) is included


def test_centres_sit_on_fixed_half_degree_lines():
    # The same place must always give the same cell, or the weather cache would miss.
    cells = corridor_cells([[(-97.13, 32.71), (-104.99, 39.74)]])

    assert cells
    assert all((lon - 0.25) % 0.5 == 0 and (lat - 0.25) % 0.5 == 0 for lon, lat in cells)


def test_a_cell_near_several_routes_is_listed_once():
    assert sorted(corridor_cells([LINE, LINE, LINE[::-1]])) == sorted(corridor_cells([LINE]))
