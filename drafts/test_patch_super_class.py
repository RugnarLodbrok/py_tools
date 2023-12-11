import pytest


class A:
    def foo(self):
        print('call A.foo()')


class B(A):
    def foo(self):
        print('call B.foo()')
        super().foo()


@pytest.fixture()
def m(mocker):
    return mocker.patch.object(A, 'foo')


def test_patch_superclass(m):
    print()
    B().foo()
    assert m.call_count == 1
