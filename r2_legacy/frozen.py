import sys
import traceback
from os.path import dirname
from os.path import join as j

import requests

from py_tools.fs import working_dir


def _is_frozen():
    if getattr(sys, 'frozen', False):  # new py2exe
        return True
    if hasattr(sys, 'importers'):  # old py2exe
        return True
    return False


FROZEN = _is_frozen()

if FROZEN:
    cacert = j(dirname(sys.argv[0]), 'cacert.pem')

    def request_get(url, auth=None, **kwargs):
        return requests.get(url, auth=auth, verify=cacert, **kwargs)

    def request_put(url, data=None, auth=None, **kwargs):
        return requests.put(url, data=data, auth=auth, verify=cacert, **kwargs)

    def request_post(url, data=None, auth=None, **kwargs):
        return requests.post(url, data=data, auth=auth, verify=cacert, **kwargs)

else:
    request_get = requests.get
    request_put = requests.put
    request_post = requests.post

if FROZEN:
    # Format traceback from certain path that contains source files to preserve actual lines
    def traceback_format_exc(limit=None, chain=True):
        with working_dir(dirname(sys.argv[0])):
            return traceback.format_exc(limit=limit, chain=chain)

    def traceback_format_exception(etype, value, tb, limit=None, chain=True):
        with working_dir(dirname(sys.argv[0])):
            return traceback.format_exception(
                etype, value, tb, limit=limit, chain=chain
            )

    def traceback_format_stack(f=None, limit=None):
        with working_dir(dirname(sys.argv[0])):
            return traceback.format_stack(f, limit)

else:
    traceback_format_exc = traceback.format_exc
    traceback_format_exception = traceback.format_exception
    traceback_format_stack = traceback.format_stack
