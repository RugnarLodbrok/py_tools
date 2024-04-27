"""
basic implementation source:
https://www.cs.mcgill.ca/~aassaf9/python/algorithm_x.html

understanding primary and secondary constrains:
http://www.nohuddleoffense.de/2019/01/20/dancing-links-algorithm-x-and-the-n-queens-puzzle/
"""

from typing import Generic, Hashable, Iterator, Mapping, Sequence, TypeVar

MAX_INT = 2147483647
P = TypeVar('P', bound=Hashable)
S = TypeVar('S', bound=Hashable)


class DancingLynx(Generic[P, S]):
    def __init__(self, pieces: Mapping[P, Sequence[S]], primary: set[S] | None = None):
        self.slots: dict[S, set[P]]
        self.pieces: dict[P, Sequence[S]]

        self.pieces = dict(pieces)
        all_slots: set[S] = set()
        for piece, slots in self.pieces.items():
            all_slots.update(slots)
        self.slots = {slot: set() for slot in all_slots}
        for piece, slots in self.pieces.items():
            for slot in slots:
                self.slots[slot].add(piece)
        self.primary = primary or set(self.slots)
        self.primary_mut = set(self.primary)

    def solve(self) -> Iterator[frozenset[P]]:
        def recur() -> Iterator[frozenset[P]]:
            if not self.primary_mut:
                yield frozenset(solution)
                return

            slot = self._shortest_slot()
            for piece in list(self.slots[slot]):
                solution.append(piece)
                cols = self.cover(piece)
                yield from recur()
                self._uncover(piece, cols)
                solution.pop()

        solution: list[P] = []
        yield from recur()

    def _shortest_slot(self) -> S:
        result = None
        shortest = MAX_INT
        for slot, pieces in self.slots.items():
            if slot not in self.primary:
                continue
            if len(pieces) < shortest:
                result = slot
                shortest = len(pieces)
        return result  # type: ignore

    def cover(self, piece: P) -> list[set[P]]:
        x: dict[S, set[P]] = self.slots
        pieces = self.pieces
        cols = []
        for slot in pieces[piece]:
            for p in x[slot]:
                for slot_ in pieces[p]:
                    if slot_ != slot:
                        x[slot_].remove(p)
            cols.append(x.pop(slot))
            if slot in self.primary:
                self.primary_mut.remove(slot)
        return cols

    def _uncover(self, piece: P, cols: list[set[P]]) -> None:
        slots = self.slots  # noqa N806
        pieces = self.pieces  # noqa N806
        for slot in reversed(pieces[piece]):
            if slot in self.primary:
                self.primary_mut.add(slot)
            slots[slot] = cols.pop()
            for p in slots[slot]:
                for slot_ in pieces[p]:
                    if slot_ != slot:
                        slots[slot_].add(p)


def dancing_lynx(
    pieces: Mapping[P, Sequence[S]], primary: set[S] | None = None
) -> Iterator[frozenset[P]]:
    """
    Algorithm X of Donald Knuth

    example input:
    {'A': [1, 4, 7],
     'B': [1, 4],
     'C': [4, 5, 7],
     'D': [3, 5, 6],
     'E': [2, 3, 6, 7],
     'F': [2, 7]}

    `slots` are `constrains` for short
    :param pieces: dict {piece: [slots]}; dict of pieces and slots of the constraints
    :param primary: set of slots; search for exact cover only for this slots;
                    all slots by default
    :return: list of solutions; solution is list of pieces
    """
    return DancingLynx(pieces, primary).solve()
