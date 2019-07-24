import inspect
import sys
import time
from contextlib import contextmanager
from functools import wraps
from hashlib import md5
from socket import gethostname, gethostbyaddr, gethostbyname, getaddrinfo, AF_INET6

WINDOWS = sys.platform == 'win32'
LINUX = sys.platform == 'linux'


def identity(x):
    return x


def retry(n=3, reraise=True, exc_type=None, sleep=None):
    def dec(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            err = None
            for _ in range(n):
                try:
                    return f(*args, **kwargs)
                except exc_type or Exception as e:
                    # logger.info("sleep before retry", seconds=sleep, error=str(e), function=f.__name__)
                    err = e
                    if sleep:
                        time.sleep(sleep)
            else:
                if reraise:
                    raise err

        return wrapper

    return dec


def file_md5(f_name):
    h = md5()
    with open(f_name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()


def get_md5(seed):
    if isinstance(seed, str):
        seed = seed.encode()
    return md5(seed).hexdigest()


def short_md5(seed):
    return get_md5(seed)[:8]


def replace_bad_chars(data, method='replace'):
    if isinstance(data, str):
        return data.encode(encoding='ASCII', errors=method).decode()
    elif isinstance(data, bytes):
        return data.decode(encoding='ASCII', errors=method).encode()
    else:
        raise TypeError("Bad data type: {}, {} or {} expected".format(type(data), str, bytes))


class EmptyClass:
    pass


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


@contextmanager
def suppress_exc(exc_type=None):
    try:
        yield
    except exc_type or Exception:
        pass


def discover_entities(module_name, cls):
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isclass(obj):
            if issubclass(obj, cls) and obj is not cls:
                yield obj


@contextmanager
def timing(msg):
    print(msg, '...', end='\r')
    t0 = time.time()
    yield
    print(msg, time.time() - t0)
