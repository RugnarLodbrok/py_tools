"""
https://leetcode.com/problems/unique-paths-iii/

On a 2-dimensional grid, there are 4 types of squares:

1 represents the starting square.  There is exactly one starting square.
2 represents the ending square.  There is exactly one ending square.
0 represents empty squares we can walk over.
-1 represents obstacles that we cannot walk over.
Return the number of 4-directional walks from the starting square to the ending square,
that walk over every non-obstacle square exactly once.



Example 1:

Input: [[1,0,0,0],[0,0,0,0],[0,0,2,-1]]
Output: 2
Explanation: We have the following two paths:
1. (0,0),(0,1),(0,2),(0,3),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2)
2. (0,0),(1,0),(2,0),(2,1),(1,1),(0,1),(0,2),(0,3),(1,3),(1,2),(2,2)
Example 2:

Input: [[1,0,0,0],[0,0,0,0],[0,0,0,2]]
Output: 4
Explanation: We have the following four paths:
1. (0,0),(0,1),(0,2),(0,3),(1,3),(1,2),(1,1),(1,0),(2,0),(2,1),(2,2),(2,3)
2. (0,0),(0,1),(1,1),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,3),(1,3),(2,3)
3. (0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(1,1),(0,1),(0,2),(0,3),(1,3),(2,3)
4. (0,0),(1,0),(2,0),(2,1),(1,1),(0,1),(0,2),(0,3),(1,3),(1,2),(2,2),(2,3)
Example 3:

Input: [[0,1],[2,0]]
Output: 0
Explanation:
There is no path that walks over every empty square exactly once.
Note that the starting and ending square can be anywhere in the grid.


Note:

1 <= grid.length * grid[0].length <= 20

"""
from typing import Iterator, Sequence, Tuple

START = 1
EMPTY = 0
END = 2
OBS = -1


class Grid:
    def __init__(self, data: Sequence[Sequence[int]]):
        self.data = data
        self.m, self.n = self._find_size(data)

        self.start, self.expected_len = self._find_start_and_expected_len()

    @staticmethod
    def _find_size(data: Sequence[Sequence[int]]) -> Tuple[int, int]:
        m = len(data)
        if not m:
            raise ValueError('Empty grid')
        n = len(data[0])
        for row in data:
            if len(row) != n:
                raise ValueError('Rows have different length')
        return m, n

    def _find_start_and_expected_len(self) -> Tuple[Tuple[int, int], int]:
        start = None
        expected_len = 2
        for i, row in enumerate(self.data):
            for j, v in enumerate(row):
                if v == START:
                    start = (i, j)
                if v == EMPTY:
                    expected_len += 1
        if start is None:
            raise ValueError('Grid has no start')
        return start, expected_len

    def _possible_steps(self, i: int, j: int) -> Iterator[Tuple[int, int]]:
        if j > 0:
            yield i, j - 1
        if j < self.n - 1:
            yield i, j + 1
        if i > 0:
            yield i - 1, j
        if i < self.m - 1:
            yield i + 1, j

    def find_paths(self):
        path = []

        def recur(i, j):
            path.append((i, j))
            if self.data[i][j] == END:
                yield path
                path.pop(-1)
                return
            self.data[i][j] = OBS
            for i_new, j_new in self._possible_steps(i, j):
                if self.data[i_new][j_new] != OBS:
                    yield from recur(i_new, j_new)
            self.data[i][j] = EMPTY
            path.pop(-1)

        for path in recur(*self.start):
            if len(path) == self.expected_len:
                yield path[:]


def main():
    for example in (
        Grid([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]),
        Grid([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]),
        Grid([[0, 1], [2, 0]]),
    ):
        for j, p in enumerate(example.find_paths()):
            print(f'{j}.\t', p)  # noqa
        print('')  # noqa


if __name__ == '__main__':
    main()
