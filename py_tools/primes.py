from copy import deepcopy
from itertools import compress, count, cycle, islice
from math import sqrt
from typing import Callable, Iterator, Sequence

import numpy as np
import numpy.typing as npt

from py_tools.seq import cons, listify


def eratosthenes(n: int) -> list[bool]:
    sieve = [True] * (n // 2 - 1)
    n_sqrt = n**0.5
    sieve_size = len(sieve)
    for i in range(sieve_size):
        if not sieve[i]:
            continue
        m = 2 * i + 3
        if m > n_sqrt:
            break

        j = (m * m - 3) // 2
        sieve[j] = False
        while j < sieve_size:
            sieve[j] = False
            j += m
    return sieve


def eratosthenes_np(n: int) -> npt.NDArray[np.bool_]:
    sieve = np.ones(n // 2 - 1, dtype=np.bool_)
    n_sqrt = n**0.5
    for i in range(n // 2 - 1):
        if not sieve[i]:
            continue
        m = 2 * i + 3
        if m > n_sqrt:
            break

        sieve[m * 3 // 2 - 1 :: m] = False
    return sieve


def primes(
    n: int, sieve_fn: Callable[[int], Sequence[bool]] = eratosthenes
) -> list[int]:
    if n < 3:
        return []
    return list(cons(2, compress(count(3, 2), sieve_fn(n))))


@listify()
def prime_factor(n: int) -> Iterator[int]:
    max_p = sqrt(n)
    for p in primes_cached:
        while not n % p:
            n //= p
            yield p
            max_p = sqrt(n)
        if p > max_p:
            break
    else:
        pass  # pylint:disable=unnecessary-pass # pragma: no cover

    if n != 1:
        yield n


def gen_primes() -> Iterator[int]:
    """
    https://stackoverflow.com/a/3796442/3367753
    """
    modulos = GenPrimes.GEN_PRIMES_MODULOS
    sieve = {9: 3, 25: 5}
    yield 2
    yield 3
    yield 5

    for q in compress(islice(count(7), 0, None, 2), cycle(GenPrimes.GEN_PRIMES_MASK)):
        p = sieve.pop(q, None)
        if p is None:
            sieve[q * q] = q
            yield q
        else:
            x = q + 2 * p
            while x in sieve or (x % 30) not in modulos:
                x += 2 * p
            sieve[x] = p
    pass  # pylint:disable=unnecessary-pass # pragma: no cover


class GenPrimes:
    GEN_PRIMES_MASK = (1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0)
    GEN_PRIMES_MODULOS = frozenset((1, 7, 11, 13, 17, 19, 23, 29))

    def __init__(self) -> None:
        self._sieve = {9: 3, 25: 5}
        self._q = 0

    def __iter__(self) -> Iterator[int]:
        for q in [2, 3, 5]:
            if self._q < q:
                self._q = q
                yield q

        sieve = self._sieve
        modulos = self.GEN_PRIMES_MODULOS

        odds = islice(count(self._q + 2), 0, None, 2)
        mask = cycle(self.GEN_PRIMES_MASK)
        mask_offset = (self._q - 5) // 2
        list(islice(mask, mask_offset % len(self.GEN_PRIMES_MASK)))

        for q in compress(odds, mask):
            if p := sieve.pop(q, None):
                x = q + 2 * p
                while x in sieve or (x % 30) not in modulos:
                    x += 2 * p
                sieve[x] = p
            else:
                sieve[q * q] = q
                self._q = q
                yield q
        pass  # pylint:disable=unnecessary-pass # pragma: no cover


class GenPrimesCached:
    def __init__(self, cache_size: int = 4096):
        if cache_size < 3:
            raise ValueError(cache_size)
        self._cache_size = cache_size
        self._cache: list[int] = []

        self._generator = GenPrimes()

    def __iter__(self) -> Iterator[int]:
        yield from self._cache
        cache_size_remain = self._cache_size - len(self._cache)
        for number in islice(self._generator, cache_size_remain):
            self._cache.append(number)
            yield number
        generator = deepcopy(self._generator)
        yield from generator


primes_cached = GenPrimesCached()
