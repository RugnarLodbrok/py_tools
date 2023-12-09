import json
import logging as lg
from contextlib import contextmanager
from copy import copy

import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import LoggerFactory, filter_by_level


def info(*args, **kwargs):
    _logger.info(*args, **kwargs)


def error(*args, **kwargs):
    _logger.error(*args, **kwargs)


class Logger:
    RABBIT_LOG_FORMAT = lg.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    FILE_LOG_FORMAT = lg.Formatter(
        '%(asctime)s %(process)d %(funcName)s [%(levelname)s]: %(message)s'
    )
    STREAM_LOG_FORMAT = lg.Formatter(
        '%(asctime)s [%(process)d]: %(message)s', datefmt='%d %H:%M:%S'
    )

    METHODS = {'debug', 'info', 'warning', 'error', 'critical', 'fatal'}

    def __init__(self):
        root = lg.getLogger()
        root.setLevel(lg.INFO)
        self.root = root

        self._loggers = [structlog.get_logger()]

    def set_level(self, level):
        return self.root.setLevel(level)

    def __getattr__(self, item):
        if item not in self.METHODS:
            raise AttributeError(item)
        return getattr(self._loggers[-1], item)

    def add_handler(self, h):
        self._remove_handler(type(h))
        return self.root.addHandler(h)

    def _remove_handler(self, handler_cls):
        for h in self.root.handlers[:]:
            if isinstance(h, handler_cls):
                self.root.removeHandler(h)

    def push_logger(self, **kwargs):
        # TODO: this is a non-thread-safe solution
        self._loggers.append(self._loggers[-1].bind(**kwargs))

    def pop_logger(self):
        self._loggers.pop()

    def inject_context(self, e):
        """
        inject current logging context to the exception
        :param e: exception
        :return:
        """
        if hasattr(e, 'kwargs'):
            kw = e.kwargs
        else:
            kw = {}
            e.kwargs = kw

        kw.update(self._loggers[-1]._context)

    @contextmanager
    def bind_logger(self, **kwargs):
        self.push_logger(**kwargs)
        try:
            yield
        except Exception as e:
            self.inject_context(e)
            raise
        finally:
            self.pop_logger()


def basic_setup():
    structlog.configure(
        processors=[
            filter_by_level,  # for performance reasons
            JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    global _logger
    h = lg.StreamHandler()
    h.setFormatter(
        StructFormatter('%(asctime)s [%(process)d]: %(message)s', datefmt='%d %H:%M:%S')
    )

    _logger = Logger()
    _logger.add_handler(h)


def format_dict(d, indent=''):
    return '\n'.join('{}{}: {}'.format(indent, k, v) for k, v in d.items())


class StructFormatter(lg.Formatter):
    def formatMessage(self, record):
        record = copy(record)
        try:
            log = json.loads(record.msg)
        except:
            pass
        else:
            message = log.pop('event', '') + '\n' + format_dict(log, '\t')
            record.msg = message
            record.message = message
        return super().formatMessage(record)


_logger = None
