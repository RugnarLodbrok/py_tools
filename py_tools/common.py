import csv
import inspect
import re
import sys
from cgi import parse_header

import json
import time

from urllib.parse import quote, urlsplit, urlunsplit
from socket import gethostname, gethostbyaddr, gethostbyname, getaddrinfo, AF_INET6
from contextlib import contextmanager
from copy import deepcopy
from functools import reduce, wraps, partial
from hashlib import md5
from io import StringIO
from itertools import chain, repeat, islice
from threading import Timer

from py_tools import logger
from py_tools.frozen import request_get

WINDOWS = sys.platform == 'win32'
LINUX = sys.platform == 'linux'


def identity(x):
    return x


filter_some = partial(filter, identity)


def retry(n=3, reraise=True, exception=None, sleep=None):
    def dec(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            err = None
            for _ in range(n):
                try:
                    return f(*args, **kwargs)
                except exception or Exception as e:
                    logger.info("sleep before retry", seconds=sleep, error=str(e), function=f.__name__)
                    err = e
                    if sleep:
                        time.sleep(sleep)
            else:
                if reraise:
                    raise err

        return wrapper

    return dec


class classproperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def file_md5(fname):
    h = md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()


def get_md5(seed):
    if isinstance(seed, str):
        seed = seed.encode()
    return md5(seed).hexdigest()


def short_md5(seed):
    return get_md5(seed)[:8]


def ignore_bad_chars(data, method='replace'):
    if isinstance(data, str):
        return data.encode(encoding='ASCII', errors=method).decode()
    elif isinstance(data, bytes):
        return data.decode(encoding='ASCII', errors=method).encode()
    else:
        raise TypeError("Bad data type: {}, {} or {} expected".format(type(data), str, bytes))


class EmptyClass(object):
    pass


def is_main_thread():
    from threading import current_thread

    try:
        from threading import main_thread
    except ImportError:
        main_thread = None

    if main_thread:
        return current_thread() is main_thread()
    else:
        from threading import _MainThread
        return isinstance(current_thread(), _MainThread)


def urlescape(url):
    scheme, netloc, path, query, fragment = urlsplit(url)
    return urlunsplit((scheme, netloc, quote(path), query, fragment))


def download_url_as_json(url, **kwargs):
    return json.loads(download_url_as_data(url, **kwargs))


def download_url_as_data(url, decode=True, auth=None, encoding=None, escape=False):
    if escape:
        url = urlescape(url)
    r = request_get(url, auth=auth)
    r.raise_for_status()
    data = r.content
    if decode:
        return data.decode(encoding or UTF8)
    return data


def download_url_as_file(url, target=None, auth=None, chunk_size=2 ** 19, escape=False):
    if escape:
        url = urlescape(url)
    r = request_get(url, auth=auth)
    r.raise_for_status()
    if not target:
        val, params = parse_header(r.headers['Content-disposition'])
        target = params['filename']
    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    return target


class Index:
    def __init__(self, lst=None):
        self._map = {}
        self.reverse_map = []
        if lst:
            for i in lst:
                x = self[i]

    def __getitem__(self, item):
        if item not in self._map:
            self._map[item] = len(self.reverse_map)
            self.reverse_map.append(item)
        return self._map[item]


def capitalize(s):
    return s[0].upper() + s[1:]


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


def zip_dicts(*dicts):
    """
    yields (key, val1, val2, val3, ...) for (dict1, dict2, dict3, ...)
    """
    for i in set(dicts[0]).intersection(*dicts[1:]):
        yield (i,) + tuple(d[i] for d in dicts)


def nth(iterable, n, default=None):
    return next(islice(iterable, n, None), default)


def zip_nth(seq, n=0):
    return nth(zip(*seq), n, default=[])


def conj(seq, v):
    yield from seq
    yield v


def get_letters(s):
    return ''.join(re.split(r"[^a-zA-Z-]*", s.strip()))


def format_dict(d, indent=''):
    return '\n'.join('{}{}: {}'.format(indent, k, v) for k, v in d.items())


def get_machine_name():
    hostname = gethostname()
    if '.' in hostname:
        return hostname
    else:
        return gethostbyaddr(hostname)[0]


def get_ip_v4(host=None):
    host = host or MACHINE_NAME
    return gethostbyname(host)


def get_ip_v6(host=None, port=0):
    host = host or MACHINE_NAME
    result = getaddrinfo(host, port, AF_INET6)
    return result[0][4][0].split('%')[0].lower()


MACHINE_NAME = get_machine_name()
MACHINE_NAME_SHORT = MACHINE_NAME.split('.')[0]
IP_V4 = get_ip_v4()
try:
    IP_V6 = get_ip_v6()
except:
    IP_V6 = None


def iter_csv_fd(f, columns=None, delimiter=','):
    r = csv.reader(f, delimiter=delimiter)
    for row in r:
        if row:
            yield islice(chain(row, repeat(None)), columns)


def iter_csv_file(f_name, columns=None, delimiter=','):
    with open(f_name, 'rt') as f:
        yield from iter_csv_fd(f, columns, delimiter)


def iter_csv_data(data, columns=None, delimiter=','):
    yield from iter_csv_fd(StringIO(data), columns, delimiter)


UTF8 = 'utf8'
CP1252 = 'cp1252'
UTF16 = 'utf16'
ENCODINGS = (UTF8, CP1252, UTF16)


def read_text_file(f_name, encoding=None, guess_encoding=False, lines=False):
    """
    :param f_name: file name
    :param encoding: encoding, determined automatically by default
    :param guess_encoding: When true return tuple (encoding, contents)
    :return: contents of file
    """

    def read(f):
        if lines:
            return [l.rstrip() for l in f.read().split('\n') if l.rstrip()]
        else:
            return f.read()

    for e in [encoding] if encoding else ENCODINGS:
        try:
            with open(f_name, 'rt', encoding=e) as f:
                if guess_encoding:
                    return e, read(f)
                return read(f)
        except UnicodeError:
            pass
    raise UnicodeError("{} couldn't open file {}".format(', '.join(ENCODINGS), f_name))


def iter_text_file(f_name, encoding=None):
    with open(f_name, 'rt', encoding=encoding or UTF8) as f:
        yield from (l.rstrip('\n\r') for l in f)


def write_text_file(f_name, content, encoding=None, lines=False):
    with open(f_name, 'wt', encoding=encoding or UTF8) as f:
        if lines:
            f.writelines(content)
        else:
            f.write(content)
    return f_name


def append_text_file(f_name, content, encoding=None):
    with open(f_name, 'at', encoding=encoding or UTF8) as f:
        f.write(content)


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


@contextmanager
def stream_redirect(stdout=True, stderr=True):
    stream = StringIO()
    so = sys.stdout
    se = sys.stderr
    sys.stdout = stream
    sys.stderr = stream
    try:
        yield stream
    finally:
        sys.stderr = se
        sys.stdout = so


def exc_to_queue(q):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                q.put(sys.exc_info())

        return wrapper

    return decorator


@contextmanager
def suppress_exc(exc_type=None):
    try:
        yield
    except exc_type or Exception:
        pass


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


def discover_entities(module_name, cls):
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isclass(obj):
            if issubclass(obj, cls) and obj is not cls:
                yield obj


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


class Timeout:
    """
    Usage:
    with Timeout(t) as t:  # time in seconds
        while t:
            do something

    Does something until time reaches t, then breaks the cycle.
    """

    def __init__(self, timeout):
        self._is_timeout = False

        if timeout:
            def foo():
                self._is_timeout = True

            self._timer = Timer(timeout, function=foo)
        else:
            self._timer = None

    def start(self):
        if self._timer is not None:
            self._timer.start()

    def __enter__(self):
        self.start()
        return self

    def __bool__(self):
        return not self._is_timeout

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
