from fractions import Fraction
from math import floor, gcd, log10
from typing import Iterator

import numpy as np

from py_tools.iter_plane import iter_quadrant_triangle


def levenshtein_distance_np(a: str, b: str) -> int:
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n

    current_row = np.linspace(
        0, n, n + 1, dtype=np.int32
    )  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row = current_row
        current_row = np.zeros(n + 1, dtype=np.int32)
        current_row[0] = i
        for j in range(1, n + 1):
            add, delete, change = (
                previous_row[j] + 1,
                current_row[j - 1] + 1,
                previous_row[j - 1],
            )
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def levenshtein_distance(a: str, b: str) -> int:
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n

    current_row = list(range(n + 1))
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = (
                previous_row[j] + 1,
                current_row[j - 1] + 1,
                previous_row[j - 1],
            )
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def levenshtein_distance2(a: str, b: str) -> int:
    columns = len(a) + 1
    rows = len(b) + 1

    # build first row
    current_row = [0]
    for column in range(1, columns):
        current_row.append(current_row[column - 1] + 1)

    for row in range(1, rows):
        previous_row = current_row
        current_row = [previous_row[0] + 1]

        for column in range(1, columns):
            insert_cost = current_row[column - 1] + 1
            delete_cost = previous_row[column] + 1

            if a[column - 1] != b[row - 1]:
                replace_cost = previous_row[column - 1] + 1
            else:
                replace_cost = previous_row[column - 1]

            current_row.append(min(insert_cost, delete_cost, replace_cost))

    return current_row[-1]


def gen_rational_numbers() -> Iterator[Fraction]:
    yield Fraction(0, 1)
    for a, b in iter_quadrant_triangle():
        a += 1
        b += 1

        if gcd(a, b) == 1:
            yield Fraction(a, b)
    pass  # pylint:disable=unnecessary-pass # pragma: no cover


def gen_fractional_approx(x: float) -> Iterator[tuple[Fraction, float]]:
    if x == 0:
        yield Fraction(0, 1), 0
        return
    if x < 0:
        for approx, error in gen_fractional_approx(-x):
            yield -approx, error
        return

    best_delta = x + 1
    num = int(x)
    den = 1

    while best_delta > 0:
        approx = Fraction(num, den)
        delta = abs(approx - x)
        if not best_delta or (delta < best_delta):
            best_delta = delta
            error = best_delta / x
            yield approx, error
        if approx < x:
            num += 1
        else:
            den += 1


def round_to_significant(x: float, n: int = 2) -> float:
    return round(x, n - 1 - floor(log10(abs(x))))
