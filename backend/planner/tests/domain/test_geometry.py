from planner.domain.geometry import simplify

TOLERANCE_M = 50


def test_points_in_a_straight_row_collapse_to_the_two_ends():
    line = ((0.0, 0.0), (0.001, 0.0), (0.002, 0.0), (0.003, 0.0))

    assert simplify(line, TOLERANCE_M) == ((0.0, 0.0), (0.003, 0.0))


def test_a_real_corner_is_kept():
    line = ((0.0, 0.0), (0.01, 0.0), (0.01, 0.01))

    assert simplify(line, TOLERANCE_M) == line


def test_a_bump_smaller_than_the_tolerance_is_removed():
    # 0.0003° of latitude is about 33 m off the straight line.
    line = ((0.0, 0.0), (0.005, 0.0003), (0.01, 0.0))

    assert simplify(line, TOLERANCE_M) == ((0.0, 0.0), (0.01, 0.0))


def test_a_bump_larger_than_the_tolerance_is_kept():
    # 0.0006° of latitude is about 67 m off the straight line.
    line = ((0.0, 0.0), (0.005, 0.0006), (0.01, 0.0))

    assert simplify(line, TOLERANCE_M) == line


def test_the_ends_never_change_even_for_a_closed_loop():
    loop = ((0.0, 0.0), (0.01, 0.0), (0.01, 0.01), (0.0, 0.0))

    simplified = simplify(loop, TOLERANCE_M)

    assert simplified[0] == (0.0, 0.0)
    assert simplified[-1] == (0.0, 0.0)
    assert (0.01, 0.0) in simplified  # the far corners are real shape
