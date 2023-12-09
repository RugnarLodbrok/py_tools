"""
https://leetcode.com/problems/substring-with-concatenation-of-all-words/

You are given a string, s, and a list of words, words, that are all of the same length.
Find all starting indices of substring(s) in s that is a concatenation of each word in
words exactly once and without any intervening characters.


Example 1:

Input:
  s = "barfoothefoobarman",
  words = ["foo", "bar"]
Output: [0, 9]
Explanation: Substrings starting at index 0 and 9 are "barfoo" and "foobar" respectively.
The output order does not matter, returning [9, 0] is fine too.


Example 2:

Input:
  s = "wordgoodgoodgoodbestword",
  words = ["word", "good", "best", "word"]
Output: []

"""
import secrets
from string import ascii_letters, digits
from time import perf_counter_ns

from non_recur import find_substring_non_recur, find_substring_non_recur2
from re_based import find_substring_re
from recur import find_substring


def main():
    for foo in [
        find_substring,
        find_substring_re,
        find_substring_non_recur,
        find_substring_non_recur2,
    ]:
        n_trials = 1000
        t0 = perf_counter_ns()
        for _ in range(n_trials):
            foo(STRING, WORDS)
        t1 = perf_counter_ns()
        t_ns = (t1 - t0) / n_trials
        print(foo.__name__, '\t', t_ns / 1e6, 'ms')


def generate_random_string(n: int) -> str:
    characters = ascii_letters + digits
    return ''.join(secrets.choice(characters) for _ in range(n))


def insert_word(string: str, word: str, idx: int) -> str:
    before = string[:idx]
    after = string[idx + len(word) :]
    return before + word + after


def make_input_string(words: list[str]) -> str:
    string = generate_random_string(256)
    for i, word in enumerate(words + words):
        idx = 16 + 32 * i
        string = insert_word(string, word, idx)
    expected_substring = ''.join(list(reversed(words))[:-1] + words)
    for idx in (20, 200):
        string = insert_word(string, expected_substring, idx)
    return string


WORDS = ['word', 'bar', 'baz', 'foo']
STRING = make_input_string(WORDS)
if __name__ == '__main__':
    main()
