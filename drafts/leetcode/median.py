# https://leetcode.com/problems/median-of-two-sorted-arrays/
from random import randrange
from typing import Iterable, TypeVar

from py_tools.seq import nth

T = TypeVar('T')


class list2(list):  # noqa N801
    def __init__(self, iterable: Iterable[T]):
        super().__init__(iterable)
        self.upper_i = len(self)
        self.lower_i = 0

    @property
    def inner_len(self) -> int:
        return self.upper_i - self.lower_i

    @property
    def lower(self) -> T:
        return self[self.lower_i]

    @property
    def upper(self) -> T:
        return self[self.upper_i - 1]


class _MedianAlgState:
    def __init__(self, a: list[int], b: list[int]):
        self.a = list2(a)
        self.b = list2(b)
        self.upper_n = 0
        self.lower_n = 0
        self.upper = None
        self.lower = None

    def solve(self) -> int:
        # 1. ranges of a and be are not intersecting
        a = self.a
        b = self.b
        assert (a[-1] <= b[0]) or (b[-1] <= a[0]), 'NIE'
        if a[0] > b[0]:
            a, b = b, a
        lower_n = 0
        upper_n = 0
        if len(a) >= len(b):
            upper_n = len(b)
            arr = a
        else:
            lower_n = len(a)
            arr = b
        while arr.inner_len > 1:
            if upper_n > lower_n:
                lower_n += arr.inner_len // 2
                arr.lower_i += arr.inner_len // 2
            else:
                upper_n += (arr.inner_len + 1) // 2
                arr.upper_i -= (arr.inner_len + 1) // 2
        return arr.lower


def median(a: list[int], b: list[int]) -> int:
    return _MedianAlgState(a, b).solve()


def my_median(a: list[int], b: list[int]) -> int:
    # slow implementation; used for validation
    def merger(a, b):
        if not a:
            yield from b
            return
        if not b:
            yield from a
            return
        a = iter(a)
        b = iter(b)
        x = next(a)
        y = next(b)
        while True:
            if x > y:
                yield y
                try:
                    y = next(b)
                except StopIteration:
                    yield x
                    yield from a
                    return
            else:
                yield x
                try:
                    x = next(a)
                except StopIteration:
                    yield y
                    yield from b
                    return

    len_2 = (len(a) + len(b)) // 2
    return nth(merger(a, b), len_2)


def median_orig(A, B):  # noqa N806
    m, n = len(A), len(B)
    if m > n:
        A, B, m, n = B, A, n, m  # noqa N806
    if n == 0:
        raise ValueError

    imin, imax, half_len = 0, m, (m + n + 1) / 2
    while imin <= imax:
        i = (imin + imax) / 2
        j = half_len - i
        if i < m and B[j - 1] > A[i]:
            # i is too small, must increase it
            imin = i + 1
        elif i > 0 and A[i - 1] > B[j]:
            # i is too big, must decrease it
            imax = i - 1
        else:
            # i is perfect

            if i == 0:
                max_of_left = B[j - 1]
            elif j == 0:
                max_of_left = A[i - 1]
            else:
                max_of_left = max(A[i - 1], B[j - 1])

            if (m + n) % 2 == 1:
                return max_of_left

            if i == m:
                min_of_right = B[j]
            elif j == n:
                min_of_right = A[i]
            else:
                min_of_right = min(A[i], B[j])

            return (max_of_left + min_of_right) / 2.0


def main():
    a = sorted(randrange(50) for _ in range(100))
    b = sorted(randrange(70, 120) for _ in range(55))
    print(f'non-intersecting:\t{median(a, b)} vs {my_median(a, b)}')
    print(f'non-intersecting:\t{median(b, a)} vs {my_median(b, a)}')

    a = sorted(randrange(70, 120) for _ in range(100))
    b = sorted(randrange(50) for _ in range(55))
    print(f'non-intersecting:\t{median(a, b)} vs {my_median(a, b)}')
    print(f'non-intersecting:\t{median(b, a)} vs {my_median(b, a)}')

    a = sorted(randrange(1000) for _ in range(100))
    b = sorted(randrange(1000) for _ in range(55))
    print(f'general case:\t{median(a, b)} vs {my_median(a, b)}')


if __name__ == '__main__':
    main()
