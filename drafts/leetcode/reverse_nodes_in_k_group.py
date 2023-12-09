from src.common.linked_list import LinkedList


def reverse_n_repeat(ll: LinkedList, n: int):
    """
    reverse every chunk of size :n: in LinkedList except remainder
    :param ll: LinkedList
    :param n: chunk size
    :return:
    """
    remaining_size = len(ll)
    node = ll.head
    node_before = None
    while remaining_size >= n:
        ll.reverse(node_before, n)
        node_before = node
        node = node.next
        remaining_size -= n


if __name__ == '__main__':
    ll = LinkedList([1, 2, 3, 4, 5, 6, 7, 8, 9])
    print(ll)
    reverse_n_repeat(ll, 3)
    print(ll)
