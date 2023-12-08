from typing import Any, Generic, Iterable, Iterator, Self, TypeVar

from py_tools.seq import isplit

T = TypeVar('T')


class ListNode(Generic[T]):
    def __init__(self, x: T):
        self.val = x
        self.next = None

    def __iter__(self) -> Self:
        curr = self
        while curr:
            yield curr
            curr = curr.next

    def __str__(self) -> str:
        def iter_for_str():
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
    def __init__(self, input_list: ListNode[T] | Iterable[T] | None = None):
        self._head: ListNode | None = None
        self._tail: ListNode | None = None
        self._len = 0
        if input_list is not None:
            for x in input_list:
                self.push_tail(x)

    @property
    def head(self) -> ListNode | None:
        return self._head

    @property
    def tail(self) -> ListNode | None:
        return self._tail

    def reverse(self, node_before: ListNode = None, n: int = None) -> None:
        """
        Reverse in one pass;
        :param node_before: a node before the chunk to be reversed. Has role
            of a pointer to the chunk
               When node_before is None; list reversed from the head;
        :param n: number of nodes to be reversed
        :return:
        """
        if node_before or (n is not None):
            self._reverse_chunk(node_before, n)
            return
        self._tail = self._head
        a = self._head
        c = None
        while a:
            b = c
            c = a
            a = c.next
            c.next = b
        self._head = c

    def _reverse_chunk(self, node_before: ListNode | None, n: int) -> None:
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
                first_node.next = a
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

    def push_tail(self, v: T):
        node = ListNode(v)
        if not self._tail:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._len += 1

    def pop_tail(self) -> T:
        raise NotImplementedError('not efficient')

    def push_head(self, v: T):
        new_head = ListNode(v)
        new_head.next = self._head
        self._head = new_head
        if not self._tail:
            self._tail = self._head
        self._len += 1

    def pop_head(self) -> T:
        if not self._len:
            raise ValueError('empty')
        r = self._head
        self._head = r.next
        if not self._head:
            self._tail = None
        self._len -= 1
        return r.val

    @classmethod
    def from_string(cls, s: str, type_: type = None) -> 'LinkedList':
        """
        example s: `1->1->2->3->4->4->5->6`
        """
        r = LinkedList()
        for v in isplit(s, '->'):
            if type_ is not None:
                v = type_(v)
            r.push_tail(v)
        return r

    def __iter__(self) -> Iterator[Any]:
        for node in self.nodes:
            yield node.val

    @property
    def nodes(self) -> Iterator[ListNode]:
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
