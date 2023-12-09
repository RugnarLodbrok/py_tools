from collections import defaultdict


def _recur(s: str, ww, i, cnt):  # pass i instead of cut string to avoid copying memory
    if not cnt:
        return True
    for w, c in ww.items():
        if not c:
            continue
        if s[i:].startswith(w):  # still we copy here :(
            ww[w] -= 1
            if _recur(s, ww, i + len(w), cnt - 1):
                ww[w] += 1
                return True
            ww[w] += 1
    return False


def find_substring(s: str, words: list[str]) -> list[int]:  # 21 us
    """
    fastest so far
    """
    ret = []
    if not words:
        return ret
    total_w_len = sum(map(len, words))
    ww = defaultdict(int)
    for w in words:
        ww[w] += 1

    for i, c in enumerate(s):
        if total_w_len + i > len(s):
            break
        if _recur(s, ww, i, len(words)):
            ret.append(i)
    return ret
