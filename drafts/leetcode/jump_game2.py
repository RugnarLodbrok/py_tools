"""
https://leetcode.com/problems/jump-game-ii/

Given an array of non-negative integers, you are initially positioned at the first index of the array.

Each element in the array represents your maximum jump length at that position.

Your goal is to reach the last index in the minimum number of jumps.

Example:

Input: [2,3,1,1,4]
Output: 2
Explanation: The minimum number of jumps to reach the last index is 2.
    Jump 1 step from index 0 to 1, then 3 steps to the last index.
Note:

You can assume that you can always reach the last index.
"""


def jump_game2(data):
    reach = 0
    reach_next = 0
    steps = 0
    for i, j in enumerate(data):
        if i > reach:
            steps += 1
            reach = reach_next
            reach_next = i
        reach_next = max(reach_next, i + j)
    return steps


if __name__ == '__main__':
    for ex in (
        [],
        [1],
        [1, 1],
        [2, 1],
        [2, 1, 1],
        [1, 2, 1],
        [2, 3, 1, 1, 4],
        [1, 1, 2, 1, 1, 1],
        [1, 5, 4, 5, 1, 2, 1, 2, 1],
    ):
        print(ex, jump_game2(ex))
