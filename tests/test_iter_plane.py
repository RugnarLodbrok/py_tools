from itertools import islice

from py_tools.iter_plane import iter_quadrant_rect, iter_quadrant_triangle


def test_iter_quadrant_rect():
    expected = [
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
        (2, 0),
        (2, 1),
        (2, 2),
        (1, 2),
        (0, 2),
        (0, 3),
        (1, 3),
        (2, 3),
        (3, 3),
        (3, 2),
        (3, 1),
        (3, 0),
    ]

    assert list(islice(iter_quadrant_rect(), 16)) == expected


def test_iter_quadrant_triangle():
    expected = [
        (0, 0),
        (0, 1),
        (1, 0),
        (2, 0),
        (1, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (2, 1),
        (3, 0),
    ]

    assert list(islice(iter_quadrant_triangle(), 10)) == expected
