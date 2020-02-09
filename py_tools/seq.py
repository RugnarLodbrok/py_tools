import re
from collections import deque
from functools import partial, wraps, reduce
from itertools import islice, tee
from copy import deepcopy


def identity(x):
    return x


filter_non_empty = partial(filter, identity)


def last(seq):
    return deque(seq, 1)[0]


def first(seq):
    return next(iter(seq))


def first_or_none(seq):
    try:
        return next(iter(seq))
    except StopIteration:
        return None


def one(seq, too_short=None, too_long=None):
    """
    one([]) -> exception
    one([1]) -> 1
    one([1, 2]) -> exception
    :param seq:
    :param too_short: exc_val
    :param too_long: exc_val
    :return:
    """
    it = iter(seq)

    try:
        value = next(it)
    except StopIteration:
        raise too_short or ValueError('too few items in iterable (expected 1)') from None

    try:
        next(it)
    except StopIteration:
        pass
    else:
        raise too_long or ValueError('too many items in iterable (expected 1)') from None

    return value


def rest(seq):
    i = iter(seq)
    next(i)
    return i


def conj(seq, v):
    yield from seq
    yield v


def cons(v, seq):
    yield v
    yield from seq


def zip_nth(seq, n=0):
    return nth(zip(*seq), n, default=[])


def nth(iterable, n, default=None):
    return next(islice(iterable, n, None), default)


def pairwise(seq):
    a, b = tee(seq)
    next(b)
    yield from zip(a, b)


def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)] * n)


def zip_dicts(*dicts):
    """
    yields (key, val1, val2, val3, ...) for (dict1, dict2, dict3, ...)
    """
    for i in set(dicts[0]).intersection(*dicts[1:]):
        yield (i,) + tuple(d[i] for d in dicts)


class MergeError(Exception):
    pass


def merge_dicts(*args, path=None):
    """
    Merge nested dicts. last one has priority over
    :param args: list of dicts to merge
    :param path: internal parameter, used for recursion
    :returns merged dict
    """
    if not args:
        return None
    if len(args) == 1:
        return args[0]
    if len(args) > 2:
        return reduce(merge_dicts, args)
    else:
        a, b = args

    path = path or []
    if a is None:
        return b
    if b is None:
        return a

    if isinstance(a, list) and isinstance(b, list):
        return a + b
    if isinstance(a, dict) and isinstance(b, dict):
        ret = deepcopy(a)
        for k, v in b.items():
            ret[k] = merge_dicts(a.get(k), v, path=path + [str(k)])
        return ret

    if type(a) != type(b):
        return b

    # raise MergeError("{}: cannot merge type {}".format('.'.join(path), type(a)))
    return b


class defaultdict2(dict):
    def __init__(self, foo, **kwargs):
        super().__init__(**kwargs)
        self._foo = foo

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            v = self._foo(item)
            self[item] = v
            return v


class key_list(list):
    def __init__(self, *args, key='name', attr=None, **kwargs):
        """
        List that allows get items by their key or attribute
        :param key:
        :param attr:
        :return:
        """
        super().__init__(*args, **kwargs)
        self.key = key
        self.attr = attr

    def __getitem__(self, item):
        if isinstance(item, int):
            return super().__getitem__(item)
        for i in self:
            if i[self.key] == item:
                return i
        raise KeyError(item)

    def get(self, item, dafault=None):
        try:
            return self[item]
        except KeyError:
            return dafault

    def __getattr__(self, item):
        for i in self:
            if getattr(i, self.attr) == item:
                return i
        raise AttributeError(item)


def listify(fn=None, wrapper=list):
    """
    A decorator which wraps a function's return value in ``list(...)``.

    Useful when an algorithm can be expressed more cleanly as a generator but
    the function should return a list.
    :param fn:
    :param wrapper:

    Example::

        >>> @listify
        ... def get_lengths(iterable):
        ...     for i in iterable:
        ...         yield len(i)
        >>> get_lengths(["spam", "eggs"])
        [4, 4]
        >>>
        >>> @listify(wrapper=tuple)
        ... def get_lengths_tuple(iterable):
        ...     for i in iterable:
        ...         yield len(i)
        >>> get_lengths_tuple(["foo", "bar"])
        (3, 3)
    """

    def listify_return(fn):
        @wraps(fn)
        def listify_helper(*args, **kw):
            return wrapper(fn(*args, **kw))

        return listify_helper

    if fn is None:
        return listify_return
    return listify_return(fn)


def isplit(source, sep=None, regex=False):
    """
    https://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python/9773142#9773142
    generator version of str.split()

    :param source:
        source string (unicode or bytes)

    :param sep:
        separator to split on.

    :param regex:
        if True, will treat sep as regular expression.

    :returns:
        generator yielding elements of string.
    """
    if sep is None:
        # mimic default python behavior
        source = source.strip()
        sep = "\\s+"
        if isinstance(source, bytes):
            sep = sep.encode("ascii")
        regex = True
    if regex:
        # version using re.finditer()
        if not hasattr(sep, "finditer"):
            sep = re.compile(sep)
        start = 0
        for m in sep.finditer(source):
            idx = m.start()
            assert idx >= start
            yield source[start:idx]
            start = m.end()
        yield source[start:]
    else:
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


def iter_plane(mode='rect', quad=True):
    """
    :param mode:
    :param quad: iter only positive indices
    """
    if mode == 'rect':
        if quad:
            return _iter_plane_rect()
        else:
            raise NotImplementedError()
    elif mode == 'triangle':
        if quad:
            return _iter_plane_triangle()
        else:
            raise NotImplementedError()
    else:
        raise ValueError(mode)


def _make_pair(a, b, swap):
    if swap:
        return b, a
    return a, b


def _iter_plane_rect():
    """
    example: for 4x4:
     1--2  9--10
        |  |  |
     4--3  8  11
     |     |  |
     5--6--7  12
              |
     16-15-14-13

    :return: [1, 2, 3, 4, ..., 16]
    """
    i = 0
    j = 0
    r = 0
    T = True

    while True:
        yield _make_pair(i, j, T)

        for _ in range(r):
            i += 1
            yield _make_pair(i, j, T)
        for _ in range(r):
            j -= 1
            yield _make_pair(i, j, T)
        r += 1
        i += 1
        j, i = i, j
        T = not T


def _iter_plane_triangle():
    """
    example: for 4x4:
     1--2  6--7
      /  /  /
     3  5  8
     |/  /
     4  9
      /
     10

    :return: [1, 2, 3, 4, ..., 16]
    """
    i = 0
    j = 0
    T = True

    while True:
        while True:
            yield _make_pair(i, j, T)
            if j == 0:
                break
            j -= 1
            i += 1
        i += 1
        i, j = j, i
        T = not T
