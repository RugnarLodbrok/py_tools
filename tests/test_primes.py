# pylint:disable=redefined-outer-name
import gzip
from itertools import islice
from pathlib import Path
from typing import Iterator

import pytest

from py_tools.primes import (
    GenPrimes,
    GenPrimesCached,
    eratosthenes,
    eratosthenes_np,
    gen_primes,
    prime_factor,
    primes,
)
from py_tools.seq import isplit, listify
from py_tools.time_utils import timing

PRIMES_FILE = Path(__file__).parent / 'primes_1_000_000.gz'
PRIME_FACTORS_FILE = Path(__file__).parent / 'prime_factors.gz'
N_PRIMES = 100_000
N_PRIME_FACTORS = 10_000


@pytest.fixture(scope='session')
@listify()
def expected_primes() -> Iterator[int]:
    data_txt = gzip.decompress(PRIMES_FILE.read_bytes()).decode()
    for line in isplit(data_txt, '\n'):
        n = int(line)
        if n >= N_PRIMES:
            break
        yield n


@pytest.fixture(scope='session')
@listify()
def expected_prime_factors() -> Iterator[tuple[int, list[int]]]:
    data_txt = gzip.decompress(PRIME_FACTORS_FILE.read_bytes()).decode()
    for line in islice(isplit(data_txt, '\n'), N_PRIME_FACTORS):
        n, *factors = (int(x) for x in line.strip().split(' '))
        yield n, factors


@pytest.mark.parametrize('sieve_fn', [eratosthenes_np, eratosthenes])
def test_primes(sieve_fn, expected_primes, logger):
    with timing() as t:
        assert primes(N_PRIMES, sieve_fn=sieve_fn) == expected_primes
    logger.info('%s %f', sieve_fn.__name__, t())


def test_prime_factor(expected_prime_factors):
    for n, factors in expected_prime_factors:
        assert prime_factor(n) == factors


@pytest.mark.parametrize('generator', [gen_primes(), GenPrimes()])
def test_gen_primes(expected_primes, logger, generator):
    with timing() as t:
        for a, b in zip(generator, expected_primes):
            assert a == b
    logger.info('gen_primes: %f', t())


@pytest.mark.parametrize('skip', [0, 1, 2, 3, 5, 20, 31, 100, 800, 1200])
def test_cached_primes_generator(expected_primes, logger, skip):
    check_window = int(skip * 1.5) + 100
    primes_cached = GenPrimesCached(cache_size=1024)
    list(islice(primes_cached, skip))

    with timing() as t:
        for a, b in zip(primes_cached, islice(expected_primes, check_window)):
            assert a == b
    logger.info('gen_primes_cached: %f', t())


def test_cached_primes_generator_generate_twice(expected_primes):
    primes_cached = GenPrimesCached(cache_size=100)
    list(islice(primes_cached, 200))
    for a, b in zip(primes_cached, islice(expected_primes, 200)):
        assert a == b


def test_primes_bad_cache():
    with pytest.raises(ValueError):
        GenPrimesCached(2)


@pytest.mark.parametrize('sieve_fn', [eratosthenes_np, eratosthenes])
@pytest.mark.parametrize(
    ('n', 'expected'),
    [
        (0, []),
        (1, []),
        (2, []),
        (3, [2]),
        (4, [2, 3]),
    ],
)
def test_corner_cases(n, expected, sieve_fn):
    assert primes(n, sieve_fn) == expected
