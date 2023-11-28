import sys
from functools import wraps
from threading import current_thread

try:
    from threading import main_thread
except ImportError:
    from threading import _MainThread as MainThread

    main_thread = None

    def is_main_thread():
        return isinstance(current_thread(), MainThread)

else:
    MainThread = None

    def is_main_thread():
        return current_thread() is main_thread()


class ExcToQueue:
    def __init__(self, q, tb_as_str=False):
        """
        Catch all exceptions and put them into queue.
        Can be used as decorator or context manager
        If given queue is multiprocessing queue, traceback should be converted to string
            because traceback cannot be pickled otherwise
        """
        self.q = q
        self.tb_as_str = tb_as_str

    def _handle(self, exc_type, exc_val, exc_tb):
        if self.tb_as_str:
            from py_tools.frozen import traceback_format_exception

            exc_tb = '\n'.join(traceback_format_exception(exc_type, exc_val, exc_tb))
        self.q.put((exc_type, exc_val, exc_tb))

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                self._handle(*sys.exc_info())

        return wrapper

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._handle(exc_type, exc_val, exc_tb)
        return True
