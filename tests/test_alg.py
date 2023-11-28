from fractions import Fraction
from itertools import islice
from math import pi

import pytest

from py_tools.alg import (
    gen_fractional_approx,
    gen_rational_numbers,
    levenshtein_distance,
    levenshtein_distance2,
    levenshtein_distance_np,
)


@pytest.mark.parametrize(
    'fn',
    [
        levenshtein_distance_np,
        levenshtein_distance,
        levenshtein_distance2,
    ],
)
def test_levenshtein_distance_np(fn):
    assert fn('apple', 'cracker') == 6
    assert fn('apple', 'appl') == 1


def test_gen_rational_numbers():
    assert list(islice(gen_rational_numbers(), 10)) == [
        Fraction(0, 1),
        Fraction(1, 1),
        Fraction(1, 2),
        Fraction(2, 1),
        Fraction(3, 1),
        Fraction(1, 3),
        Fraction(1, 4),
        Fraction(2, 3),
        Fraction(3, 2),
        Fraction(4, 1),
    ]


def test_gen_fractional_approx():
    assert list(islice(gen_fractional_approx(pi), 10)) == [
        (Fraction(0, 1), 1.0),
        (Fraction(1, 1), 1.46694220692426),
        (Fraction(2, 1), 2.751938393884109),
        (Fraction(3, 1), 22.187539917793156),
        (Fraction(13, 4), 28.979518064229662),
        (Fraction(16, 5), 53.78762855490349),
        (Fraction(19, 6), 125.2927739950566),
        (Fraction(22, 7), 2484.4755386294846),
        (Fraction(179, 57), 2529.9181572934895),
        (Fraction(201, 64), 3246.608793402466),
    ]
