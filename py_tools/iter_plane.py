from typing import Iterator


def iter_quadrant_rect() -> Iterator[tuple[int, int]]:
    """
    example: for 4x4:
     1--2  9--10
        |  |  |
     4--3  8  11
     |     |  |
     5--6--7  12
              |
     16-15-14-13

    :return: [1, 2, 3, 4, ..., 16]
    """
    i = 0
    j = 0
    radius = 0
    transposed = True

    while True:
        yield (j, i) if transposed else (i, j)

        for _ in range(radius):
            i += 1
            yield (j, i) if transposed else (i, j)
        for _ in range(radius):
            j -= 1
            yield (j, i) if transposed else (i, j)
        radius += 1
        i += 1
        j, i = i, j
        transposed = not transposed


def iter_quadrant_triangle() -> Iterator[tuple[int, int]]:
    """
    example: for 4x4:
     1--2  6--7
      /  /  /
     3  5  8
     |/  /
     4  9
      /
     10

    :return: [1, 2, 3, 4, ..., 16]
    """
    i = 0
    j = 0
    transposed = True

    while True:
        while True:
            yield (j, i) if transposed else (i, j)
            if j == 0:
                break
            j -= 1
            i += 1
        i += 1
        i, j = j, i
        transposed = not transposed
