"""
https://leetcode.com/problems/trapping-rain-water/

Given n non-negative integers representing an elevation map where the width of each bar
is 1, compute how much water it is able to trap after raining.

The above elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1]. In this case,
6 units of rain water (blue section) are being trapped. Thanks Marcos for contributing
this image!

Example:

Input: [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6

"""
import json
from itertools import count
from typing import List


def trap(height):
    water = 0
    max_height_left = 0
    for x, h in enumerate(height[1:], start=1):
        print(f'{x}/{len(height)}')  # noqa
        if h > height[x - 1]:
            for h2 in range(height[x - 1] + 1, h + 1):
                if h2 > max_height_left:
                    break
                for i in count(x - 1, -1):
                    if i < 0:
                        break
                    if height[i] >= h2:
                        water += x - i - 1
                        break
        max_height_left = max(max_height_left, h)
    return water


def trap2(nums: List[int]) -> int:
    l, r = 0, len(nums) - 1
    res, h = 0, 0

    while l < r:
        # the current water level
        h = max(h, min(nums[l], nums[r]))
        if nums[l] < nums[r]:
            l += 1
            if h - nums[l] > 0:
                res += h - nums[l]
        else:
            r -= 1
            if h - nums[r] > 0:
                res += h - nums[r]

    return res


if __name__ == '__main__':
    print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # noqa
    print('expected: 6')  # noqa

    with open('rain_input.json', 'rt') as f:
        print(trap(json.load(f)))  # noqa
