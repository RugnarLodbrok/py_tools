import csv
import json
import sys
import requests
from cgi import parse_header
from contextlib import contextmanager
from io import StringIO
from itertools import islice, chain, repeat
from urllib.parse import urlsplit, urlunsplit, quote

UTF8 = 'utf8'
CP1252 = 'cp1252'
UTF16 = 'utf16'
ENCODINGS = (UTF8, CP1252, UTF16)


def iter_csv_fd(f, columns=None, delimiter=','):
    r = csv.reader(f, delimiter=delimiter)
    for row in r:
        if row:
            yield islice(chain(row, repeat(None)), columns)


def iter_csv_file(f_name, columns=None, delimiter=',', encoding=UTF8):
    with open(f_name, 'rt', encoding=encoding) as f:
        yield from iter_csv_fd(f, columns, delimiter)


def iter_csv_data(data, columns=None, delimiter=','):
    yield from iter_csv_fd(StringIO(data), columns, delimiter)


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


@contextmanager
def stream_redirect(stdout=True, stderr=True):
    stream = StringIO()
    so = sys.stdout
    se = sys.stderr
    if stdout:
        sys.stdout = stream
    if stderr:
        sys.stderr = stream
    try:
        yield stream
    finally:
        sys.stderr = se
        sys.stdout = so


def urlescape(url):
    scheme, netloc, path, query, fragment = urlsplit(url)
    return urlunsplit((scheme, netloc, quote(path), query, fragment))


def download_url_as_json(url, **kwargs):
    return json.loads(download_url_as_data(url, **kwargs))


def download_url_as_data(url, decode=True, auth=None, encoding=None, escape=False):
    if escape:
        url = urlescape(url)
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    data = r.content
    if decode:
        return data.decode(encoding or UTF8)
    return data


def download_url_as_file(url, target=None, auth=None, chunk_size=2 ** 19, escape=False):
    if escape:
        url = urlescape(url)
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    if not target:
        val, params = parse_header(r.headers['Content-disposition'])
        target = params['filename']
    with open(target, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    return target
