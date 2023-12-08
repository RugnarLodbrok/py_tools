from typing import Any, Iterable, Iterator, TypeVar, Generic, Self

from py_tools.seq import isplit, nth

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

    def __repr__(self):
        if self.next:
            if self.next.next:
                return f'[{self.val}]->[{self.next.val}]->...'
            return f'[{self.val}]->[{self.next.val}]'
        return f'[{self.val}]'


class LinkedList(Generic[T]):
    def __init__(self, input_list: ListNode[T] | Iterable[T] | None = None):
        self.head = None  # todo: getter
        self.tail = None  # todo getter
        self._len = 0  # todo: private
        if input_list is not None:
            for x in input_list:
                self.push_tail(x)

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
        self.tail = self.head
        a = self.head
        c = None
        while a:
            b = c
            c = a
            a = c.next
            c.next = b
        self.head = c

    def _reverse_chunk(self, node_before: ListNode | None, n: int) -> None:
        if n is None:
            n = len(self)
        if node_before:
            first_node = node_before.next
        else:
            first_node = self.head
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
            self.tail = first_node
        if node_before:
            node_before.next = c
        else:
            self.head = c

    def push_tail(self, v: T):
        node = ListNode(v)
        if not self.tail:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._len += 1

    def pop_tail(self) -> T:
        raise NotImplementedError('not efficient')

    def push_head(self, v: T):
        new_head = ListNode(v)
        new_head.next = self.head
        self.head = new_head
        if not self.tail:
            self.tail = self.head
        self._len += 1

    def pop_head(self) -> T:
        if not self._len:
            raise ValueError('empty')
        r = self.head
        self.head = r.next
        if not self.head:
            self.tail = None
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
        if self.head:
            yield from iter(self.head)

    def __len__(self) -> int:
        return self._len

    def __bool__(self) -> bool:
        return not not self._len

    def __str__(self) -> str:
        if not self:
            return '<Empty LL>'

        def iter_for_str():
            seen = set()
            for i, node in enumerate(self.nodes):
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


MAX_PRINT_LENGTH = 256
