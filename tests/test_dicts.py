# pylint:disable=invalid-name
from py_tools.dicts import defaultdict2, merge_dicts, zip_dicts


def test_zip_dicts():
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 3, 'b': 4, 'c': 5}
    assert dict(zip_dicts(d1, d2)) == {'a': [1, 3], 'b': [2, 4]}
    assert dict(zip_dicts(d1, d2, union=True)) == {'a': [1, 3], 'b': [2, 4], 'c': [5]}


def test_defaultdict2():
    d = defaultdict2(int)  # type:ignore[type-var]
    assert d[0] == 0
    assert d['1'] == 1
    assert d['33'] == 33


def test_merge_dicts():
    assert merge_dicts() == {}
    assert merge_dicts({'a': 1}) == {'a': 1}
    assert merge_dicts({'a': 1}, {'b': 2}) == {'a': 1, 'b': 2}
    assert merge_dicts({'a': [1]}, {'a': [2]}, {'a': [3]}) == {'a': [1, 2, 3]}
    assert merge_dicts({'a': [1]}, {'a': 'x'}) == {'a': 'x'}
    assert merge_dicts({'a': 1}, {'a': None}) == {'a': 1}
    assert merge_dicts({'content': {'a': 1}}, {'content': {'b': 2}}) == {
        'content': {'a': 1, 'b': 2}
    }
