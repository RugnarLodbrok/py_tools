from fractions import Fraction
from collections import defaultdict
from itertools import count
from math import sqrt, gcd

from py_tools.seq import iter_plane


def levenshtein_distance(a, b):
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    assert isinstance(a, str) and isinstance(b, str), "{} and {}".format(type(a), type(b))
    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
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


def get_primes3(n):
    for x in primes():
        if x > n:
            break
        yield x


def get_primes4(n):
    for x in primes(n):
        if x > n:
            break
        yield x


def primes(n=None):
    """Sieve of Eratosthenes"""
    D = defaultdict(list)  # map composite integers to primes witnessing their compositeness
    if n:
        sqrt_n = int(sqrt(n))
        for q in count(2):
            if q not in D:
                yield q
                if q <= sqrt_n:
                    D[q * q] = [q]

            else:
                for p in D[q]:
                    if q + p > n and False:
                        break
                    D[p + q].append(p)
                del D[q]
    else:
        for q in count(2):
            if q not in D:
                yield q  # not marked composite, must be prime
                D[q * q] = [q]  # first multiple of q not already marked

            else:
                for p in D[q]:  # move each witness to its next multiple
                    D[p + q].append(p)
                del D[q]  # no longer need D[q], free memory


def get_primes(n):
    m = n + 1
    numbers = [True] * m
    for i in range(2, int(n ** 0.5 + 1)):
        if numbers[i]:
            for j in range(i * i, m, i):
                numbers[j] = False
    primes = []
    for i in range(2, m):
        if numbers[i]:
            primes.append(i)
    return primes


def get_primes2(n):
    if n == 2:
        return [2]
    elif n < 2:
        return []
    s = list(range(3, n + 1, 2))
    mroot = n ** 0.5
    half = (n + 1) // 2 - 1
    i = 0
    m = 3
    while m <= mroot:
        if s[i]:
            j = (m * m - 3) // 2
            s[j] = 0
            while j < half:
                s[j] = 0
                j += m
        i = i + 1
        m = 2 * i + 3
    return [2] + [x for x in s if x]


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


def bench_primes():
    import time
    from memory_profiler import memory_usage

    from py_tools.seq import listify

    N_validation = 1000
    N = int(3e6)

    for f in (
            get_primes,
            get_primes2,
            listify(get_primes3),
            listify(get_primes4),
    ):
        for a, b in zip(f(N_validation), get_primes(N_validation)):
            assert a == b

        start = time.time()
        f(N)
        print(f.__name__, time.time() - start, end="\t")

        print("mem =", memory_usage((f, (N,)), max_usage=True)[0])
        # for x in mem:
        #     print(f"{int(x)}\t", end="")
        # print("")


if __name__ == '__main__':
    bench_primes()
