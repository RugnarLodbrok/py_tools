import re
from collections import defaultdict


def find_substring_re(s: str, words: list[str]) -> list[int]:  # 33 us
    """
    non-recursive, based on regex
    """
    ret = []
    if not words:
        return ret
    total_w_len = sum(map(len, words))
    ww = defaultdict(int)
    for w in words:
        ww[w] += 1

    def recur(i):  # pass i instead of cut string to avoid copying memory
        words = {**ww}
        while True:
            words_pattern = '|'.join(w for w, c in words.items() if c)
            if not words_pattern:
                return True
            match = re.match(fr'^.{{{i}}}({words_pattern})', s)
            if not match:
                return False
            w = match.group(1)
            words[w] -= 1
            i += len(w)

    for m in re.finditer('(' + '|'.join(ww) + ')', s):
        i = m.start()
        if total_w_len + i > len(s):
            break
        if recur(i):
            ret.append(i)
    return ret
