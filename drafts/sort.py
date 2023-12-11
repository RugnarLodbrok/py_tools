from random import randint

from py_tools.time import timing


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
    def merge(start, mid, end):
        a = arr[start:mid]
        b = arr[mid:end]
        p = start
        p1 = 0
        p2 = 0
        a_len = len(a)
        b_len = len(b)
        while p1 < a_len and p2 < b_len:
            if a[p1] < b[p2]:
                arr[p] = a[p1]
                p1 += 1
            else:
                arr[p] = b[p2]
                p2 += 1
            p += 1
        while p1 < a_len:
            arr[p] = a[p1]
            p1 += 1
            p += 1
        while p2 < b_len:
            arr[p] = b[p2]
            p2 += 1
            p += 1

    def recur(start, end):
        if end - start > 2:
            mid = (end + start) // 2
            recur(start, mid)
            recur(mid, end)
            merge(start, mid, end)
        else:
            if arr[start] > arr[end - 1]:
                arr[start], arr[start + 1] = arr[start], arr[start + 1]

    recur(0, len(a))


if __name__ == '__main__':
    q_times = []
    m_times = []
    for _ in range(200):
        a = [randint(0, 150000) for _ in range(30000)]
        tmp = a[:]
        with timing() as t:
            mergesort(tmp)
        m_times.append(t())

        tmp = a[:]
        with timing() as t:
            qsort(tmp)
        q_times.append(t())

    print('merge', sum(m_times) / len(m_times))
    print('qsort', sum(q_times) / len(q_times))

"""
merge 0.030498292117845268
qsort 0.025943265575915576
remove swap call
merge 0.02992545232642442
qsort 0.025914575769566
remove comment and unused func
merge 0.029527431223541498
qsort 0.025833900645375253

"""
