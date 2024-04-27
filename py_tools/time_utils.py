import time
from contextlib import contextmanager
from typing import Callable, Iterator


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


class Swatch:
    def __init__(self, time_function: Callable[[], float] = time.time):
        self.time_function = time_function
        self.t = time_function()

    def __call__(self) -> float:
        t = self.time_function()
        dt = t - self.t
        self.t = t
        return dt  # noqa: R504

    def wait(self, dt: float) -> None:
        t = self.time_function()
        t_passed = t - self.t
        t_remains = dt - t_passed
        if t_remains > 0:
            time.sleep(t_remains)


swatch = Swatch()
