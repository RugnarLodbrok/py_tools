from fractions import Fraction
from math import gcd, sqrt
from itertools import count, compress

try:
    import numpy as np
except ImportError:
    np = None
try:
    import numba
except ImportError:
    numba = None
from py_tools.seq import iter_plane, cons, listify

if np:
    def levenshtein_distance(a, b):
        n, m = len(a), len(b)
        if n > m:
            a, b = b, a
            n, m = m, n

        current_row = np.linspace(0, n, n + 1, dtype=np.int32)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row = current_row
            current_row = np.zeros(n + 1, dtype=np.int32)
            current_row[0] = i
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)
        return current_row[n]
else:
    def levenshtein_distance(a, b):
        n, m = len(a), len(b)
        if n > m:
            a, b = b, a
            n, m = m, n

        current_row = range(n + 1)
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)
        return current_row[n]


def levenshtein_distance2(a, b):
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


def gen_rational_numbers():
    yield Fraction(0, 1)
    for a, b in iter_plane('triangle'):
        a += 1
        b += 1

        if gcd(a, b) == 1:
            yield Fraction(a, b)


def gen_fractional_approx(n):
    delta = None
    num = 0
    den = 1

    while True:
        r = Fraction(num, den)
        delta2 = abs(r - n)
        if not delta or (delta2 < delta):
            delta = delta2
            yield r, n / delta
        if r < n:
            num += 1
        else:
            den += 1


if not np:
    def primes(n):
        if n == 2:
            return [2]
        elif n < 2:
            return []
        sieve = [True] * (n // 2 - 1)
        mroot = n ** 0.5
        half = (n + 1) // 2 - 1
        for i in count():
            m = 2 * i + 3
            if m > mroot:
                break

            if sieve[i]:
                j = (m * m - 3) // 2
                sieve[j] = False
                while j < half:
                    sieve[j] = False
                    j += m
        return list(cons(2, compress(count(3, 2), sieve)))
else:
    def primes(n):
        if n == 2:
            return [2]
        elif n < 2:
            return []
        sieve = np.ones(n // 2, dtype=bool)
        sieve[0] = False
        mroot = n ** 0.5
        for i in count():
            m = 2 * i + 1
            if m > mroot:
                break
            if sieve[i]:
                sieve[m * 3 // 2::m] = False

        # use np.compress?
        return list(cons(2, compress(count(1, 2), sieve)))
    #  TODO: add the fastest numba impl


@listify
def prime_factor(n):
    for p in primes(int(sqrt(n) + 1)):
        while not n % p:
            n //= p
            yield p
    if n != 1:
        yield n
