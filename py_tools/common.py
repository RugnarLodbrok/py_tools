import inspect
import re
import sys
import time
from contextlib import contextmanager
from functools import wraps
from hashlib import md5
from socket import gethostname, gethostbyaddr, gethostbyname, getaddrinfo, AF_INET6
from threading import Timer

WINDOWS = sys.platform == 'win32'
LINUX = sys.platform == 'linux'


def identity(x):
    return x


def retry(n=3, reraise=True, exception=None, sleep=None):
    from py_tools import logger
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
