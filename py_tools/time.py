import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator

AnyDict = dict[str, Any]


@contextmanager
def timing() -> Iterator[Callable[[], float]]:
    def get_time() -> float:
        if t1 is None:
            raise RuntimeError  # pragma: no cover
        return t1 - t0

    t1 = None
    t0 = time.perf_counter()
    yield get_time
    t1 = time.perf_counter()
