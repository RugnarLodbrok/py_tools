import pytest


class A:
    def foo(self) -> list:
        raise NotImplementedError


@pytest.fixture(autouse=True)
def mutable_return_value(mocker):
    return mocker.patch.object(
        A,
        'foo',
        autospec=True,
        return_value=[],
    )


def test_test1():
    assert A().foo() == []
    A().foo().append(0)
    assert A().foo() == [0]
