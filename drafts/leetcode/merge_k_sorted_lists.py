from typing import Callable, List, Sequence, TypeVar

from src.common.linked_list import LinkedList, ListNode

T = TypeVar('T')


def insort(a: list[T], x: T, key: Callable[[T], int] = None):
    i = 0
    j = len(a)
    if key:
        while i < j:
            mid = (i + j) // 2
            if key(x) <= key(a[mid]):
                j = mid
            else:
                i = mid + 1
    else:
        while i < j:
            mid = (i + j) // 2
            if x <= a[mid]:
                j = mid
            else:
                i = mid + 1
    a.insert(i, x)
    return i


def merge(lists: Sequence[LinkedList]):
    r = LinkedList()

    def key_f(lst: LinkedList):
        return -lst.head.val

    lists = [lst for lst in lists if lst.head]
    lists = sorted(lists, key=key_f)
    while lists:
        current_list = lists.pop()
        r.push_tail(current_list.pop_head())
        if current_list:
            insort(lists, current_list, key=key_f)
    return r


class Solution:
    def merge_lists(self, lists: List[ListNode]) -> ListNode:
        return merge([LinkedList(x) for x in lists]).head


def main():
    lists = [
        LinkedList.from_string('1->4->5', type_=int),
        LinkedList.from_string('2->6', type_=int),
        LinkedList.from_string('1->3->4', type_=int),
    ]

    heads = [llist.head for llist in lists]

    print(LinkedList(Solution().merge_lists(heads)))

    print(LinkedList(Solution().merge_lists([lst.head for lst in [LinkedList()]])))


if __name__ == '__main__':
    main()
