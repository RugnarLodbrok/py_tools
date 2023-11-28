import logging

import pytest
from pytest_logger.plugin import LoggerConfig


@pytest.fixture()
def iterable():
    def _iterable():
        yield 1
        yield 2
        yield 3

    return _iterable()


@pytest.fixture()
def logger():
    return logging.getLogger('test_logger')


def pytest_logger_config(logger_config: LoggerConfig):
    logger_config.add_loggers(['test_logger'], stdout_level='info')
    logger_config.set_log_option_default('test_logger')
