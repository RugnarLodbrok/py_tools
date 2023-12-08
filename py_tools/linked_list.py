from __future__ import annotations

from typing import Any, Callable, Generic, Iterable, Iterator, Self, TypeVar, overload

from py_tools.seq import isplit

T = TypeVar('T')


class ListNode(Generic[T]):
    def __init__(self, x: T):
        self.val: T = x
        self.next: Self | None = None

    def __iter__(self) -> Iterator[Self]:
        curr: Self | None = self
        while curr:
            yield curr
            curr = curr.next

    def __str__(self) -> str:
        def iter_for_str() -> Iterator[str]:
            seen = set()
            for i, node in enumerate(self):
                if i >= MAX_PRINT_LENGTH:
                    yield '...'
                    return
                if node not in seen:
                    yield f'[{str(node.val)}]'
                    seen.add(node)
                else:
                    yield f'(loop)[{str(node.val)}]'
                    return

        return '->'.join(iter_for_str())

    __repr__ = __str__


class LinkedList(Generic[T]):
    def __init__(self, input_list: Iterable[T] | None = None):
        self._head: ListNode[T] | None = None
        self._tail: ListNode[T] | None = None
        self._len = 0
        if input_list is not None:
            for x in input_list:
                self.push_tail(x)

    @property
    def head(self) -> ListNode[T] | None:
        return self._head

    @property
    def tail(self) -> ListNode[T] | None:
        return self._tail

    def reverse(
        self, node_before: ListNode[T] | None = None, n: int | None = None
    ) -> None:
        """
        Reverse in one pass;
        :param node_before: a node before the chunk to be reversed. Has role
            of a pointer to the chunk
               When node_before is None; list reversed from the head;
        :param n: number of nodes to be reversed
        :return:
        """
        if n is None:
            n = len(self)
        if node_before:
            first_node = node_before.next
        else:
            first_node = self._head
        a = first_node
        c = None
        while a:
            if not n:  # chunk ended
                first_node.next = a  # type: ignore
                break
            b = c
            c = a
            a = c.next
            c.next = b
            n -= 1
        else:  # list ended
            self._tail = first_node
        if node_before:
            node_before.next = c
        else:
            self._head = c

    def push_tail(self, v: T) -> None:
        node = ListNode(v)
        if not self._tail:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._len += 1

    def pop_tail(self) -> T:
        raise NotImplementedError('not efficient')

    def push_head(self, v: T) -> None:
        new_head = ListNode(v)
        new_head.next = self._head
        self._head = new_head
        if not self._tail:
            self._tail = self._head
        self._len += 1

    def pop_head(self) -> T:
        if not self._head:
            raise ValueError('empty')
        old_head = self._head
        self._head = old_head.next
        if not self._head:
            self._tail = None
        self._len -= 1
        return old_head.val

    @classmethod
    @overload
    def from_string(cls, string: str, type_: None = None) -> LinkedList[str]:
        ...

    @classmethod
    @overload
    def from_string(cls, string: str, type_: Callable[[str], T]) -> LinkedList[T]:
        ...

    @classmethod
    @overload
    def from_string(cls, string: str, type_: type[T]) -> LinkedList[T]:
        ...

    @classmethod
    def from_string(cls, string: str, type_: Callable[[str], T] | None = None) -> Any:
        """
        example s: `1->1->2->3->4->4->5->6`
        """
        lst: LinkedList[T | str] = LinkedList()
        for v in isplit(string, '->'):
            if type_ is not None:
                lst.push_tail(type_(v))
            else:
                lst.push_tail(v)
        return lst

    def __iter__(self) -> Iterator[T]:
        for node in self.nodes:
            yield node.val

    @property
    def nodes(self) -> Iterator[ListNode[T]]:
        if self._head:
            yield from iter(self._head)

    def __len__(self) -> int:
        return self._len

    def __bool__(self) -> bool:
        return not not self._len

    def __str__(self) -> str:
        if not self:
            return '<Empty LL>'

        return str(self._head)

    __repr__ = __str__


MAX_PRINT_LENGTH = 256
