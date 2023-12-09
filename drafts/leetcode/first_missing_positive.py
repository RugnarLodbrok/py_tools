"""
https://leetcode.com/problems/first-missing-positive/

Given an unsorted integer array, find the smallest missing positive integer.

Example 1:

Input: [1,2,0]
Output: 3
Example 2:

Input: [3,4,-1,1]
Output: 2
Example 3:

Input: [7,8,9,11,12]
Output: 1
Note:

Your algorithm should run in O(n) time and uses constant extra space.

"""

MAX_INT = 2147483647


def fmp(a):
    for i in range(len(a)):
        if a[i] <= 0:
            a[i] = MAX_INT
    for n in a:
        if n < 0:
            n *= -1
        if n > len(a):
            continue
        if a[n - 1] < 0:
            continue
        a[n - 1] *= -1
    for i, n in enumerate(a):
        if n >= 0:
            return i + 1
    return len(a) + 1


if __name__ == '__main__':
    for i, o in [
        ([1, 2, 0], 3),
        ([3, 4, -1, 1], 2),
        ([7, 8, 9, 11, 12], 1),
        ([], 1),
        ([1], 2),
        ([1, 1], 2),
        ([3, 4, -1, 1], 2),
        ([-5, 1000], 1),
        ([0, 1, 2], 3),
        ([-1, 1, 2], 3),
    ]:
        my_o = fmp(i[:])
        if my_o == o:
            print('[OK]\t', i, o)
        else:
            print('[ERR]\t', i, o, my_o)
