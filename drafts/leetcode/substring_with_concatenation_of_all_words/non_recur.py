from collections import defaultdict
from dataclasses import dataclass


@dataclass
class State:
    i: int
    j: int = 0
    recur: bool = False


@dataclass
class WordCount:
    word: str
    count: int


def find_substring_non_recur2(s: str, words: list[str]) -> list[int]:  # noqa
    """
    the slowest but doesn't fail when len(words) > python stack size
    """
    ret = []
    if not words:
        return ret
    ww = defaultdict(int)
    for w in words:
        ww[w] += 1
    ww = [WordCount(word=w, count=c) for w, c in ww.items()]
    total_w_len = sum(map(len, words))

    def non_recur(i: int, cnt: int):
        stack = [State(i=i)]  # (j)
        ans = False
        while stack:
            if len(stack) > cnt:
                ans = True
            state = stack[-1]

            if state.recur:
                ww[state.j].count += 1
                state.j += 1
            while state.j < len(ww):
                w = ww[state.j]
                if not w.count:
                    state.j += 1
                    continue
                if s[state.i :].startswith(w.word):
                    w.count -= 1
                    state.recur = True
                    stack.append(State(i=state.i + len(w.word)))
                    break
                state.j += 1
            else:
                stack.pop(-1)
        return ans

    cnt = len(words)
    for i, c in enumerate(s):
        if total_w_len + i > len(s):
            break
        if non_recur(i, cnt):
            ret.append(i)
    return ret


def find_substring_non_recur(s: str, words: list[str]) -> list[int]:  # noqa
    """
    the slowest but doesn't fail when len(words) > python stack size
    """
    ret = []
    if not words:
        return ret
    ww = defaultdict(int)
    for w in words:
        ww[w] += 1
    ww = [{'word': w, 'count': c} for w, c in ww.items()]
    total_w_len = sum(map(len, words))

    def non_recur(i, cnt):
        stack = [{'i': i}]  # (j)
        ans = False
        while stack:
            if len(stack) > cnt:
                ans = True
            state = stack[-1]

            state.setdefault('j', 0)
            state.setdefault('recur', False)
            if state['recur']:
                ww[state['j']]['count'] += 1
                state['j'] += 1
            while state['j'] < len(ww):
                w = ww[state['j']]
                if not w['count']:
                    state['j'] += 1
                    continue
                if s[state['i'] :].startswith(w['word']):
                    w['count'] -= 1
                    state['recur'] = True
                    stack.append({'i': state['i'] + len(w['word'])})
                    break
                state['j'] += 1
            else:
                stack.pop(-1)
        return ans

    cnt = len(words)
    for i, c in enumerate(s):
        if total_w_len + i > len(s):
            break
        if non_recur(i, cnt):
            ret.append(i)
    return ret
