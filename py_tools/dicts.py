from copy import deepcopy
from functools import reduce
from typing import Any, Callable, Hashable, Iterator, Tuple, TypeVar, overload

from py_tools.time import AnyDict

T = TypeVar('T')
V = TypeVar('V')
K = TypeVar('K', bound=Hashable)


@overload
def _merge_two_dicts(a: None, b: T) -> T:
    ...


@overload
def _merge_two_dicts(a: T, b: None) -> T:
    ...


@overload
def _merge_two_dicts(a: list[T], b: list[T]) -> list[T]:
    ...


@overload
def _merge_two_dicts(a: dict[K, V], b: dict[K, V]) -> dict[K, V]:
    ...


def _merge_two_dicts(a: Any, b: Any) -> Any:
    if a is None:
        return b
    if b is None:
        return a

    if isinstance(a, list) and isinstance(b, list):
        return a + b
    if isinstance(a, dict) and isinstance(b, dict):
        ret = deepcopy(a)
        for k, v in b.items():
            ret[k] = _merge_two_dicts(a.get(k), v)
        return ret

    return b


def merge_dicts(*args: AnyDict) -> AnyDict:
    """
    Merge nested dicts. last one has priority over
    :param args: list of dicts to merge
    :param path: internal parameter, used for recursion
    :returns merged dict
    """
    if not args:
        return {}
    if len(args) == 1:
        return args[0]
    return reduce(_merge_two_dicts, args)


def zip_dicts(*dicts: dict[T, V], union: bool = False) -> Iterator[Tuple[T, list[V]]]:
    if union:
        keys = set(dicts[0]).union(*dicts[1:])
    else:
        keys = set(dicts[0]).intersection(*dicts[1:])
    for k in keys:
        yield k, [d[k] for d in dicts if k in d]


class defaultdict2(dict[K, V]):  # noqa  # pylint:disable=invalid-name
    def __init__(self, foo: Callable[[K], V]):
        super().__init__()
        self._foo = foo

    def __getitem__(self, item: K) -> V:
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self._foo(item)
            self[item] = value
            return value
