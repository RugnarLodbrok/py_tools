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
    assert list(gen_fractional_approx(0)) == [(Fraction(0, 1), 0)]
    assert list(gen_fractional_approx(5.5)) == [
        (Fraction(5, 1), 0.09090909090909091),
        (Fraction(11, 2), 0.0),
    ]
    assert list(islice(gen_fractional_approx(pi), 7)) == [
        (Fraction(3, 1), 0.04507034144862795),
        (Fraction(13, 4), 0.034507130097319726),
        (Fraction(16, 5), 0.018591635788130244),
        (Fraction(19, 6), 0.007981306248670453),
        (Fraction(22, 7), 0.0004024994347707008),
        (Fraction(179, 57), 0.0003952697035345213),
        (Fraction(201, 64), 0.0003080137040323832),
    ]
    assert list(gen_fractional_approx(-0.768)) == [
        (Fraction(0, 1), 1.0),
        (Fraction(-1, 1), 0.3020833333333333),
        (Fraction(-2, 3), 0.1319444444444445),
        (Fraction(-3, 4), 0.02343750000000002),
        (Fraction(-7, 9), 0.012731481481481477),
        (Fraction(-10, 13), 0.0016025641025641374),
        (Fraction(-33, 43), 0.0007267441860464921),
        (Fraction(-43, 56), 0.00018601190476186363),
        (Fraction(-53, 69), 0.0001509661835748186),
        (Fraction(-96, 125), 0.0),
    ]
