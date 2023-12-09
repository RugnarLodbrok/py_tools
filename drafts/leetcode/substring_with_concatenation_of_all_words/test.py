import pytest

from .non_recur import find_substring_non_recur
from .re_based import find_substring_re
from .recur import find_substring

LARGE_STRING = (
    'cHOYZAZbqVD4UopywordfoobazbarwordbarbazfooviOfkebar1bixL8h8vQV9U'
    '4IrMeMHwoLUIvri6bazgo26fJiatmIl7F6Ywd0iVC5V3ejARfoot8Fx1HnxVrC4d'
    'Z6DnlhWcOMdf29uhwordEw8iDrFLW2iT95AIiVjWxqwmg8XSbarhhcWULyq15SHk'
    'enx4zSNpfoobazbarwordbarbazfooYQMHAW3dH81Wd0uMlHfooMij19fg0NZDvw'
)
LARGE_STRING_WORDS = ['word', 'bar', 'baz', 'foo']


@pytest.mark.parametrize(
    ('string', 'words', 'expected'),
    [
        ('barfoothebarfoobarman', ['foo', 'bar'], [0, 9, 12]),
        ('a' * 36, ['a'] * 8, list(range(29))),
        ('barfoothebarfoobarman', [], []),
        ('wordgoodgoodgoodbestword', ['word', 'good', 'best', 'word'], []),
        ('a' * 100, ['a'] * 101, []),
        ('a' * 500, ['a'] * 499, [0, 1]),
        ('a' * 5000, ['a'] * 5001, []),
        (LARGE_STRING, LARGE_STRING_WORDS, [16, 20, 29, 200, 209]),
    ],
)
@pytest.mark.parametrize(
    'function', [find_substring_re, find_substring_non_recur, find_substring]
)
def test(function, string, words, expected):
    assert function(string, words) == expected
