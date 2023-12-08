# pylint:disable=redefined-outer-name
import pytest

from py_tools import linked_list
from py_tools.linked_list import LinkedList


@pytest.fixture()
def cycled_list():
    lst = LinkedList(range(4))
    _, node1, _, node3 = lst.nodes
    node3.next = node1
    return lst


@pytest.fixture()
def _fake_max_print_length():
    value = linked_list.MAX_PRINT_LENGTH
    linked_list.MAX_PRINT_LENGTH = 5
    yield
    linked_list.MAX_PRINT_LENGTH = value


def test_create():
    lst = LinkedList(range(5))
    assert str(lst) == '[0]->[1]->[2]->[3]->[4]'
    assert list(lst) == list(range(5))


@pytest.mark.parametrize(
    ('lst', 'expected'),
    [
        (LinkedList(range(3)), [0, 1, 2, 8, 9]),
        (LinkedList([]), [8, 9]),
    ],
)
def test_push_tail(lst, expected):
    lst.push_tail(8)
    lst.push_tail(9)
    assert list(lst) == expected
    assert lst.tail.val == 9


@pytest.mark.parametrize(
    ('lst', 'expected'),
    [
        (LinkedList(range(3)), [8, 9, 0, 1, 2]),
        (LinkedList([]), [8, 9]),
    ],
)
def test_pop_push_head(lst, expected):
    initial = list(lst)
    lst.push_head(9)
    lst.push_head(8)
    assert list(lst) == expected
    assert lst.pop_head() == 8
    assert lst.pop_head() == 9
    assert list(lst) == initial


def test_pop_head_empty():
    lst: LinkedList[int] = LinkedList([])
    with pytest.raises(ValueError):
        lst.pop_head()


def test_from_str():
    lst = LinkedList.from_string('1->1->2->3->4->4->5->6')
    assert list(lst) == list(map(str, [1, 1, 2, 3, 4, 4, 5, 6]))
    lst2 = LinkedList.from_string('1->1->2->3->4->4->5->6', type_=int)
    assert list(lst2) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_len():
    assert len(LinkedList([])) == 0
    assert len(LinkedList([1])) == 1
    assert len(LinkedList(range(10))) == 10


def test_reverse():
    lst = LinkedList(range(10))
    lst.reverse()

    assert list(lst) == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    lst.reverse(node_before=lst.head.next.next.next)  # type: ignore
    assert list(lst) == [9, 8, 7, 6, 0, 1, 2, 3, 4, 5]
    lst.reverse(n=4)
    assert list(lst) == [6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
    lst.reverse(node_before=lst.head.next.next.next, n=5)  # type: ignore
    assert list(lst) == [6, 7, 8, 9, 4, 3, 2, 1, 0, 5]

    lst = LinkedList()
    lst.reverse()
    assert not lst

    lst = LinkedList([1, 2])
    lst.reverse(node_before=lst.tail)
    assert list(lst) == [1, 2]


@pytest.mark.usefixtures('_fake_max_print_length')
def test_str(cycled_list):
    assert str(LinkedList(range(10))) == '[0]->[1]->[2]->[3]->[4]->...'
    assert str(cycled_list) == '[0]->[1]->[2]->[3]->(loop)[1]'
    assert str(LinkedList([])) == '<Empty LL>'
    assert str(LinkedList()) == '<Empty LL>'
