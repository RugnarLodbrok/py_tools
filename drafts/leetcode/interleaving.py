"""
https://leetcode.com/problems/interleaving-string/

Given s1, s2, s3, find whether s3 is formed by the interleaving of s1 and s2.

Example 1:

Input: s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"
Output: true
Example 2:

Input: s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"
Output: false
"""

import numpy as np


def interleaving_naive(s1, s2, s3):
    len1 = len(s1)
    len2 = len(s2)
    len3 = len(s3)

    def recur(i, j, k):
        while k < len3:
            if i < len1 and j < len2 and s1[i] == s2[j]:
                if s1[i] != s3[k]:
                    return False
                return recur(i + 1, j, k + 1) or recur(i, j + 1, k + 1)

            if i < len1 and s1[i] == s3[k]:
                k += 1
                i += 1

            elif j < len2 and s2[j] == s3[k]:
                k += 1
                j += 1
            else:
                return False

        return (i == len1) and (j == len2) and (k == len3)

    return recur(0, 0, 0)


def interleaving_dynamic(s1, s2, s3):
    if len(s1) + len(s2) != len(s3):
        return False

    if len(s1) < len(s2):
        s2, s1 = s1, s2

    current = None
    for j in range(len(s2) + 1):
        previous = current
        current = np.zeros(len(s1) + 1, dtype=np.bool)
        for i in range(len(s1) + 1):
            if i == 0 and j == 0:
                current[i] = True
            elif i == 0:
                current[i] = previous[i] and s2[j - 1] == s3[j - 1]
            elif j == 0:
                current[i] = current[i - 1] and s1[i - 1] == s3[i - 1]
            else:
                current[i] = (previous[i] and s2[j - 1] == s3[i + j - 1]) or (
                    current[i - 1] and s1[i - 1] == s3[i + j - 1]
                )
    return current[-1]


if __name__ == '__main__':
    interleaving = interleaving_dynamic
    print(interleaving(s1='ab', s2='bc', s3='bbac'))
    print(interleaving(s1='', s2='', s3=''))
    print(interleaving(s1='db', s2='b', s3='cbb'))
    print(interleaving(s1='aabcc', s2='dbbca', s3='aadbbcbcac'))
    print(interleaving(s1='dbbca', s2='aabcc', s3='aadbbcbcac'))
    print(interleaving(s1='aabcc', s2='dbbca', s3='aadbbbaccc'))
    print(
        interleaving(
            *[
                (
                    'bbbbbabbbbabaababaaaabbababbaaabbabbaaabaaaaababbbababbbbbabbbbababba'
                    'baabababbbaabababababbbaaababaa'
                ),
                (
                    'babaaaabbababbbabbbbaabaabbaabbbbaabaaabaababaaaabaaabbaaabaaaabaabaa'
                    'bbbbbbbbbbbabaaabbababbabbabaab'
                ),
                (
                    'babbbabbbaaabbababbbbababaabbabaabaaabbbbabbbaaabbbaaaaabbbbaabbaaaba'
                    'babbaaaaaabababbababaababbababbbababbbbaaaabaabbabbaaaaabbabbaaaabbba'
                    'abaaabaababaababbaaabbbbbabbbbaabbabaabbbbabaaabbababbabbabbab'
                ),
            ]
        )
    )
