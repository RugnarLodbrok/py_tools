from functools import cached_property


class A:
    def __init__(self):
        self.cnt = 0

    @cached_property
    def foo(self):
        self.cnt += 1
        return self.cnt


def test_cached_property():
    a = A()
    assert a.foo == 1
    assert a.foo == 1
    del a.foo  # proper cache delete
    assert a.foo == 2
    assert a.foo == 2
    a.foo = None  # improper cache delete
    assert a.foo is None
    assert a.cnt == 2
