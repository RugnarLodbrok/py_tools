"""
https://leetcode.com/problems/grid-illumination/

On an N x N grid of cells, each cell (x, y) with 0 <= x < N and 0 <= y < N has a lamp.

Initially, some number of lamps are on.  lamps[i] tells us the location of the i-th lamp
 that is on.  Each lamp that is on illuminates every square on its x-axis, y-axis, and
 both diagonals (similar to a Queen in chess).

For the i-th query queries[i] = (x, y), the answer to the query is 1 if the cell (x, y)
 is illuminated, else 0.

After each query (x, y) [in the order given by queries], we turn off any lamps that are
 at cell (x, y) or are adjacent 8-directionally (ie., share a corner or edge with cell
  (x, y).)

Return an array of answers.  Each value answer[i] should be equal to the answer of the
 i-th query queries[i].



Example 1:

Input: N = 5, lamps = [[0,0],[4,4]], queries = [[1,1],[1,0]]
Output: [1,0]
Explanation:
Before performing the first query we have both lamps [0,0] and [4,4] on.
The grid representing which cells are lit looks like this, where [0,0] is the top left
 corner, and [4,4] is the bottom right corner:
1 1 1 1 1
1 1 0 0 1
1 0 1 0 1
1 0 0 1 1
1 1 1 1 1
Then the query at [1, 1] returns 1 because the cell is lit.  After this query, the lamp
 at [0, 0] turns off, and the grid now looks like this:
1 0 0 0 1
0 1 0 0 1
0 0 1 0 1
0 0 0 1 1
1 1 1 1 1
Before performing the second query we have only the lamp [4,4] on.  Now the query
 at [1,0] returns 0, because the cell is no longer lit.

Note:
    1. 1 <= N <= 10^9
    2. 0 <= lamps.length <= 20000
    3. 0 <= queries.length <= 20000
    4. lamps[i].length == queries[i].length == 2

"""
from collections import defaultdict
from typing import Sequence, Tuple


def grid_illumination(  # noqa C901
    n: int,
    lamps: Sequence[Tuple[int, int]],
    queries: Sequence[Tuple[int, int]],
):
    lamps_x = defaultdict(set)
    lamps_y = defaultdict(int)
    lamps_r = defaultdict(int)
    lamps_l = defaultdict(int)
    for x, y in lamps:
        lamps_x[x].add((x, y))
        lamps_y[y] += 1
        lamps_r[x - y] += 1
        lamps_l[x + y] += 1

    def check_illumination(x, y):
        return int(
            not not (lamps_x[x] or lamps_y[y] or lamps_l[x + y] or lamps_r[x - y])
        )

    def remove_lamp(i, j):
        if i == 0:
            x_min = 0
        else:
            x_min = i - 1
        if i == n:
            x_max = n
        else:
            x_max = i + 1

        if j == 0:
            y_min = 0
        else:
            y_min = j - 1
        if j == n:
            y_max = n
        else:
            y_max = j + 1

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                lamp = (x, y)
                if lamp in lamps_x[x]:
                    lamps_x[x].remove(lamp)
                    lamps_y[y] -= 1
                    lamps_r[x - y] -= 1
                    lamps_l[x + y] -= 1

    ret = []
    for q in queries:
        ret.append(check_illumination(*q))
        remove_lamp(*q)

    return ret


if __name__ == '__main__':
    print(grid_illumination(5, [(0, 0), (4, 4)], [(1, 1), (1, 0)]))
