from random import randint


def qsort(arr):
    def recur(start, end):
        i = start
        j = end
        side = 0
        while i != j:
            if arr[i] > arr[j]:
                arr[i], arr[j] = arr[j], arr[i]
                side = not side
            if side:
                i += 1
            else:
                j -= 1
        if start < i - 1:
            recur(start, i - 1)
        if i + 1 < end:
            recur(i + 1, end)

    recur(0, len(a) - 1)


def mergesort(arr):
    def recur(start, end):
        if start - end > 2:  # noqa R509  #pylint:disable=no-else-raise
            mid = (end - start) // 2
            recur(start, mid)
            recur(mid, end)
            raise NotImplementedError('too difficult to do in-place')  # merge
        else:
            if arr[start] > arr[start + 1]:
                arr[start], arr[start + 1] = arr[start + 1], arr[start]

    recur(0, len(a))


if __name__ == '__main__':
    a = [randint(-50, 150) for _ in range(300)]
    print(a)
    qsort(a)
    print(a)
