from typing import Any, Callable, Generic, TypeVar

T = TypeVar('T')
C = TypeVar('C')


class classproperty(Generic[T, C], property):  # noqa: N801 pylint:disable=C0103
    """stolen from sqlalchemy.util.classproperty"""

    fget: Callable[[type[C]], T]

    def __init__(self, fget: Callable[[type[C]], T], *arg: Any, **kw: Any):
        super().__init__(fget, *arg, **kw)
        self.__doc__ = fget.__doc__

    def __get__(self, obj: None, cls: type[C] | None = None) -> T:
        if cls is None:
            raise RuntimeError  # pragma: no cover
        return self.fget(cls)
