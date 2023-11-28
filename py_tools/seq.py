import re
from collections import deque
from functools import partial, wraps
from itertools import islice, tee
from typing import (
    Any,
    AnyStr,
    Callable,
    Container,
    Iterable,
    Iterator,
    ParamSpec,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

T = TypeVar('T')
P = ParamSpec('P')


def identity(x: T) -> T:
    return x


def exhaust(seq: Iterable[Any]) -> None:
    deque(seq, 0)


filter_non_empty: Callable[[Iterable[T]], Iterator[T]] = partial(filter, identity)


def last(seq: Iterable[T]) -> T:
    return deque(seq, 1)[0]


def first(seq: Iterable[T]) -> T:
    return next(iter(seq))


def first_or_none(seq: Iterable[T]) -> T | None:
    try:
        return next(iter(seq))
    except StopIteration:
        return None


def one(seq: Iterable[T]) -> T:
    iterator = iter(seq)

    try:
        value = next(iterator)
    except StopIteration:
        raise ValueError('expected exactly 1 item') from None

    try:
        next(iterator)
    except StopIteration:
        pass
    else:
        raise ValueError('expected exactly 1 item') from None

    return value


def rest(seq: Iterable[T]) -> Iterator[T]:
    iterator = iter(seq)
    next(iterator)
    return iterator


def conj(seq: Iterable[T], item: T) -> Iterator[T]:
    yield from seq
    yield item


def cons(item: T, seq: Iterable[T]) -> Iterator[T]:
    yield item
    yield from seq


def zip_nth(seq: Iterable[Sequence[T]], n: int = 0) -> Tuple[T, ...]:
    return nth(zip(*seq), n, default=())  # type:ignore


def nth(iterable: Iterable[T], n: int, default: T | None = None) -> T | None:
    return next(islice(iterable, n, None), default)


def pairwise(seq: Iterable[T]) -> Iterator[Tuple[T, T]]:
    a, b = tee(seq)
    try:
        next(b)
    except StopIteration:
        return
    yield from zip(a, b)


def chunks(iterable: Iterable[T], n: int) -> Iterator[list[T]]:
    if n < 1:
        raise ValueError(n)
    iterator = iter(iterable)
    while True:
        chunk = list(islice(iterator, n))
        if not chunk:
            break
        yield chunk


def listify(
    container: Type = list,  # type:ignore[type-arg]
) -> Callable[[Callable[P, Iterator[T]]], Callable[P, Container[T]]]:
    """
    A decorator which wraps a function's return value in ``list(...)``.

    Useful when an algorithm can be expressed more cleanly as a generator but
    the function should return a list.
    :param fn:
    :param container:

    Example::

        >>> @listify()
        ... def get_lengths(iterable):
        ...     for i in iterable:
        ...         yield len(i)
        >>> get_lengths(["spam", "eggs"])
        [4, 4]
        >>>
        >>> @listify(container=tuple)
        ... def get_lengths_tuple(iterable):
        ...     for i in iterable:
        ...         yield len(i)
        >>> get_lengths_tuple(["foo", "bar"])
        (3, 3)
    """

    def listify_decorator(fn: Callable[P, Iterator[T]]) -> Callable[P, Container[T]]:
        @wraps(fn)
        def wrapper(*args: P.args, **kw: P.kwargs) -> Container[T]:
            return container(fn(*args, **kw))

        return wrapper

    return listify_decorator


def isplit(
    source: AnyStr, sep: AnyStr | re.Pattern[AnyStr] | None, regex: bool = False
) -> Iterator[AnyStr]:
    """
    https://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python/9773142#9773142
    generator version of str.split()
    """
    if sep is None:
        # mimic default python behavior
        source = source.strip()
        if isinstance(source, bytes):
            sep = b'\\s+'
        else:
            sep = '\\s+'
        regex = True
    if regex:
        return _isplit_regex(source, sep)
    if not isinstance(sep, (str, bytes)):
        raise TypeError(type(sep))
    return _isplit_non_regex(source, sep)


def _isplit_non_regex(source: AnyStr, sep: AnyStr) -> Iterator[AnyStr]:
    # version using str.find(), less overhead than re.finditer()
    sepsize = len(sep)
    start = 0
    while True:
        idx = source.find(sep, start)
        if idx == -1:
            yield source[start:]
            return
        yield source[start:idx]
        start = idx + sepsize


def _isplit_regex(source: AnyStr, sep: AnyStr | re.Pattern[AnyStr]) -> Iterator[AnyStr]:
    # version using re.finditer()
    if isinstance(sep, bytes | str):
        sep = re.compile(sep)
    start = 0
    for match in sep.finditer(source):
        idx = match.start()
        assert idx >= start
        yield source[start:idx]
        start = match.end()
    yield source[start:]
