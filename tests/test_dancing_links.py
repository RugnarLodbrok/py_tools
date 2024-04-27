from itertools import compress, count, product
from typing import Iterator

import pytest

from py_tools.dancing_links import DancingLynx, dancing_lynx
from py_tools.seq import exhaust


@pytest.mark.parametrize(
    ('primary_constraints', 'solutions'),
    [
        ({1}, [['A'], ['B']]),
        ({1, 2}, [['B', 'F'], ['B', 'E']]),
        (set(range(1, 8)), [['B', 'D', 'F']]),
    ],
)
def test_basic(primary_constraints, solutions):
    pieces = {
        'A': [1, 4, 7],
        'B': [1, 4],
        'C': [4, 5, 7],
        'D': [3, 5, 6],
        'E': [2, 3, 6, 7],
        'F': [2, 7],
    }
    result = dancing_lynx(pieces, primary=primary_constraints)

    expected = {frozenset(solution) for solution in solutions}
    assert set(result) == expected


@pytest.mark.parametrize(
    ('n', 'solutions'),
    [
        (0, set()),
        (1, {frozenset({(0, 0)})}),
        (2, set()),
        (3, set()),
        (
            4,
            {
                frozenset({(1, 0), (0, 2), (2, 3), (3, 1)}),
                frozenset({(0, 1), (3, 2), (1, 3), (2, 0)}),
            },
        ),
        (
            5,
            {
                frozenset({(3, 4), (0, 3), (2, 2), (1, 0), (4, 1)}),
                frozenset({(2, 4), (1, 2), (4, 3), (3, 1), (0, 0)}),
                frozenset({(0, 1), (4, 4), (2, 0), (3, 2), (1, 3)}),
                frozenset({(0, 1), (4, 3), (1, 4), (3, 0), (2, 2)}),
                frozenset({(4, 0), (2, 1), (1, 4), (0, 2), (3, 3)}),
                frozenset({(3, 4), (2, 1), (0, 0), (4, 2), (1, 3)}),
                frozenset({(2, 4), (4, 0), (1, 1), (0, 3), (3, 2)}),
                frozenset({(4, 4), (3, 1), (2, 3), (0, 2), (1, 0)}),
                frozenset({(1, 2), (0, 4), (2, 0), (3, 3), (4, 1)}),
                frozenset({(0, 4), (1, 1), (4, 2), (3, 0), (2, 3)}),
            },
        ),
        (
            6,
            {
                frozenset({(2, 4), (3, 1), (0, 3), (4, 5), (1, 0), (5, 2)}),
                frozenset({(1, 2), (0, 4), (4, 3), (2, 0), (5, 1), (3, 5)}),
                frozenset({(0, 1), (5, 4), (4, 2), (3, 0), (2, 5), (1, 3)}),
                frozenset({(4, 0), (2, 1), (3, 4), (1, 5), (0, 2), (5, 3)}),
            },
        ),
    ],
)
def test_queens(n, solutions):
    assert {frozenset(solution) for solution in queens(n)} == solutions


@pytest.mark.parametrize(
    ('n', 'n_solutions'),
    [
        (0, 0),
        (1, 1),
        (2, 0),
        (3, 0),
        (4, 2),
        (5, 10),
        (6, 4),
        (7, 40),
        (8, 92),
        (9, 352),
        (10, 724),
        (11, 2680),
        (12, 14200),
    ],
)
def test_queens_solution_count(n, n_solutions):
    if n > 10:
        return
    assert sum(1 for _ in queens(n)) == n_solutions


def test_sudoku():
    sudoku = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    exhaust(sudoku_dancing_links(sudoku))
    assert sudoku == [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


def _queens_make_constraint(n: int, i: int, j: int) -> list[bool]:
    column = [False] * n
    row = [False] * n
    left_diagonal = [False] * (2 * n - 3)
    right_diagonal = [False] * (2 * n - 3)

    column[i] = True
    row[j] = True

    d_left = i + j - 1
    # omit diagonals of length of 1
    if not (d_left == -1 or d_left == len(left_diagonal)):
        left_diagonal[d_left] = True

    d_right = j - i + n - 2
    # omit diagonals of length of 1
    if not (d_right == -1 or d_right == len(right_diagonal)):
        right_diagonal[d_right] = True

    return column + row + left_diagonal + right_diagonal


def queens(n: int) -> Iterator[frozenset[tuple[int, int]]]:
    if n == 1:
        yield frozenset([(0, 0)])
    if n <= 1:
        return

    pieces: dict[tuple[int, int], list[bool]] = {}
    for i, j in product(range(n), range(n)):
        pieces[(i, j)] = _queens_make_constraint(n, i, j)

    pieces_compressed = {  # convert boolean mask to indices
        piece: list(compress(count(), slots_mask))
        for piece, slots_mask in pieces.items()
    }
    yield from dancing_lynx(pieces_compressed, primary=set(range(2 * n)))


def sudoku_dancing_links(data: list[list[int]]) -> Iterator[None]:
    """
    3ms
    """
    n = 9
    pieces: dict[tuple[int, int, int], list[tuple[str, tuple[int, int]]]] = {}
    for row, col, n in product(range(n), range(n), range(1, n + 1)):
        box = (row // 3) * 3 + (col // 3)  # Box number
        pieces[(row, col, n)] = [
            ('rc', (row, col)),  # row and column
            ('rn', (row, n)),  # row and number
            ('cn', (col, n)),  # column and number
            ('bn', (box, n)),  # box and number
        ]
    dancing_links = DancingLynx(pieces)

    # `y` defines the rules of sudoku in general;
    # the code below populates data for the given board
    for i, j in product(range(n), range(n)):
        if data[i][j]:
            dancing_links.cover((i, j, data[i][j]))

    for solution in dancing_links.solve():
        for i, j, v in solution:
            data[i][j] = v
        yield
