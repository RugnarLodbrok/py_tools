"""
https://leetcode.com/problems/n-queens/

The n-queens puzzle is the problem of placing n queens on an n×n chessboard such that no
two queens attack each other.



Given an integer n, return all distinct solutions to the n-queens puzzle.

Each solution contains a distinct board configuration of the n-queens' placement, where
'Q' and '.' both indicate a queen and an empty space respectively.

Example:

Input: 4
Output: [
 [".Q..",  // Solution 1
  "...Q",
  "Q...",
  "..Q."],

 ["..Q.",  // Solution 2
  "Q...",
  "...Q",
  ".Q.."]
]
Explanation: There exist two distinct solutions to the 4-queens puzzle as shown above.
"""
from itertools import product, compress, count
from typing import Iterator

from py_tools.dancing_links import dancing_lynx


def _make_constraint(n: int, i: int, j: int) -> list[bool]:
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


def queens(n: int) -> Iterator[list[tuple[int, int]]]:
    if n == 1:
        yield [(0, 0)]
    if n <= 1:
        return

    pieces: dict[tuple[int, int], list[bool]] = {}
    for i, j in product(range(n), range(n)):
        pieces[(i, j)] = _make_constraint(n, i, j)

    pieces_compressed = {
        piece: list(compress(count(), slots_mask))
        for piece, slots_mask in pieces.items()
    }
    yield from dancing_lynx(pieces_compressed, primary=set(range(2 * n)))


def format_solutions(n: int) -> Iterator[str]:
    for solution in queens(n):
        r = [['.'] * n for _ in range(n)]
        for i, j in solution:
            r[i][j] = 'Q'

        yield '\n'.join(''.join(x) for x in r)


def test_queens() -> None:
    assert {frozenset(solution) for solution in queens(5)} == {
        frozenset([(0, 1), (4, 3), (1, 4), (3, 0), (2, 2)]),
        frozenset([(0, 1), (4, 4), (2, 0), (3, 2), (1, 3)]),
        frozenset([(1, 2), (0, 4), (2, 0), (3, 3), (4, 1)]),
        frozenset([(0, 4), (1, 1), (4, 2), (3, 0), (2, 3)]),
        frozenset([(3, 4), (2, 1), (0, 0), (4, 2), (1, 3)]),
        frozenset([(2, 4), (1, 2), (4, 3), (3, 1), (0, 0)]),
        frozenset([(2, 4), (4, 0), (1, 1), (0, 3), (3, 2)]),
        frozenset([(3, 4), (0, 3), (2, 2), (1, 0), (4, 1)]),
        frozenset([(4, 0), (2, 1), (1, 4), (0, 2), (3, 3)]),
        frozenset([(4, 4), (3, 1), (2, 3), (0, 2), (1, 0)]),
    }
