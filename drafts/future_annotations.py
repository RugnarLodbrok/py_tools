from __future__ import annotations

from copy import deepcopy


class A:
    def copy(self) -> A:
        return deepcopy(self)
