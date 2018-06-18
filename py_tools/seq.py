from copy import deepcopy
from functools import reduce, partial, wraps
from itertools import islice

from collections import deque

from py_tools.common import identity


def last(seq):
    return deque(seq, 1)[0]


def first(seq):
    return next(iter(seq))


def conj(seq, v):
    yield from seq
    yield v


def zip_nth(seq, n=0):
    return nth(zip(*seq), n, default=[])


def nth(iterable, n, default=None):
    return next(islice(iterable, n, None), default)


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


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


filter_some = partial(filter, identity)


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
