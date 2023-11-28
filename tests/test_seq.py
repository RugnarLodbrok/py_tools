import re

import pytest

from py_tools.seq import (
    chunks,
    conj,
    cons,
    exhaust,
    filter_non_empty,
    first,
    first_or_none,
    isplit,
    last,
    nth,
    one,
    pairwise,
    rest,
    zip_nth,
)


def test_exhaust(iterable):
    exhaust(iterable)
    assert not list(iterable)


def test_filter_non_empty():
    seq = ['a', 1, 0, '', 'b', None, -1]
    assert list(filter_non_empty(seq)) == ['a', 1, 'b', -1]


def test_first(iterable):
    assert first(iterable) == 1
    assert list(iterable) == [2, 3]


def test_first_or_none(iterable):
    assert first_or_none(iterable) == 1
    assert first_or_none([]) is None


def test_last(iterable):
    assert last(iterable) == 3


def test_one(iterable):
    with pytest.raises(ValueError):
        one([])
    assert one([1]) == 1

    with pytest.raises(ValueError):
        one(iterable)
    assert one(iterable) == 3
    with pytest.raises(ValueError):
        one(iterable)


def test_rest(iterable):
    assert list(rest(iterable)) == [2, 3]


def test_conj(iterable):
    assert list(conj(iterable, 0)) == [1, 2, 3, 0]


def test_cons(iterable):
    assert list(cons(0, iterable)) == [0, 1, 2, 3]


@pytest.mark.parametrize(('idx', 'result'), [(0, 1), (1, 2), (4, None)])
def test_nth(iterable, idx, result):
    assert nth(iterable, idx) == result


def test_zip_nth(iterable):
    assert zip_nth([(1, 2), (3, 4)]) == (1, 3)
    assert zip_nth([(1, 2), (3, 4)], 1) == (2, 4)
    assert zip_nth([iterable, ('a', 'b')]) == (1, 'a')
    assert zip_nth([iterable, ('a', 'b')], 2) == ()


def test_pairwise(iterable):
    assert not list(pairwise([]))
    assert not list(pairwise([1]))
    assert list(pairwise([1, 2])) == [(1, 2)]
    assert list(pairwise(iterable)) == [(1, 2), (2, 3)]


def test_chunks():
    assert list(chunks(range(10), 3)) == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    with pytest.raises(ValueError, match='0'):
        list(chunks([], 0))


@pytest.mark.parametrize(
    ('string', 'sep', 'expected', 'regex'),
    [
        ('a b', None, ['a', 'b'], False),
        (b'a b', None, [b'a', b'b'], False),
        ('a\tb', None, ['a', 'b'], False),
        ('acb', None, ['acb'], False),
        ('acb', 'c', ['a', 'b'], False),
        (b'acb', b'c', [b'a', b'b'], False),
        (b'acb', b'c', [b'a', b'b'], True),
        ('a b', None, ['a', 'b'], True),
        ('a\tb', None, ['a', 'b'], True),
        ('acb', None, ['acb'], True),
        ('acb', 'c', ['a', 'b'], True),
        ('a1bc2d', '[12]', ['a', 'bc', 'd'], True),
        ('a1bc2d', re.compile('[12]'), ['a', 'bc', 'd'], True),
    ],
)
def test_isplit(string, sep, expected, regex):
    assert list(isplit(string, sep=sep, regex=regex)) == expected


def test_isplit_bad_args():
    with pytest.raises(TypeError):
        list(isplit('a b', re.compile(' ')))
