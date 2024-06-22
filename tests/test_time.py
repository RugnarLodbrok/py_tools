# pylint:disable=redefined-outer-name
import pytest

from py_tools.time_utils import Swatch


@pytest.fixture()
def fake_time():
    x = 0

    def time():
        nonlocal x
        t = x * x
        x += 1
        return t

    return time


@pytest.fixture()
def fake_sleep(mocker):
    return mocker.patch('py_tools.time_utils.time.sleep')


def test_swatch(fake_time, fake_sleep):
    swatch = Swatch(time_function=fake_time)
    assert swatch() == 1
    assert swatch() == 3
    assert swatch() == 5
    swatch.wait(20)
    swatch.wait(0)
    fake_sleep.assert_called_once_with(13)
