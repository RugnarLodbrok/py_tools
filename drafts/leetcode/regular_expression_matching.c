/*

https://leetcode.com/problems/regular-expression-matching/

Given an input string (s) and a pattern (p), implement regular expression matching with support for '.' and '*'.

'.' Matches any single character.
'*' Matches zero or more of the preceding element.
The matching should cover the entire input string (not partial).

Note:

s could be empty and contains only lowercase letters a-z.
p could be empty and contains only lowercase letters a-z, and characters like . or *.
Example 1:

Input:
s = "aa"
p = "a"
Output: false
Explanation: "a" does not match the entire string "aa".
Example 2:

Input:
s = "aa"
p = "a*"
Output: true
Explanation: '*' means zero or more of the preceding element, 'a'. Therefore, by repeating 'a' once, it becomes "aa".
Example 3:

Input:
s = "ab"
p = ".*"
Output: true
Explanation: ".*" means "zero or more (*) of any character (.)".
Example 4:

Input:
s = "aab"
p = "c*a*b"
Output: true
Explanation: c can be repeated 0 times, a can be repeated 1 time. Therefore, it matches "aab".
Example 5:

Input:
s = "mississippi"
p = "mis*is*p*."
Output: false
*/

static unsigned int ft_strlen(char *str)
{
	int len;

	len = 0;
	while (*(str + len) != '\0')
	{
		len++;
	}
	return (len);
}

static unsigned int star_count(char *str)
{
	int n;

	n = 0;
	while (*str)
		if (*str++ == '*')
			n++;
	return (n);
}

static int recur(char *s, char *p, unsigned int star_len)
{
	unsigned int i;
	unsigned int n;

	n = 0;
	while (1)
	{
		if (*p && p[1] == '*')  // current char is asketisked
		{
			i = -1;
			while (++i <= star_len)  //star_len + 1  tris;  0..star_len
			{
				if (i && (s[i - 1] != *p && *p != '.'))
					break;
				if (recur(s + i, p + 2, star_len - i))
					return (1);
			}
			return (0); //  asterisk didn't match
		}
		if (!*s)
			return (!*p);
		if (!*p)
			return (0);
		if (*s != *p && *p != '.')
			return (0);
		s++;
		p++;
	}
}

int nmatch(char *s1, char *s2)
{
	return (recur(s1, s2, ft_strlen(s1) - ft_strlen(s2) + star_count(s2)));
}

bool isMatch(char *s, char *p)
{
	//assume there's never more then one asterisk in a row
	int star_len = ft_strlen(s) - ft_strlen(p) + 2 * star_count(p);
	//total length of asterisk-matched characters
	if (star_len < 0)
		return (0);
	return recur(s, p, star_len);
}

int main(int ac, char **av)
{
	char *p = av[1];
	char *s = av[2];
	printf("`%s` matches `%s`: %d\n", p, s, isMatch(s, p));
	return 0;
}
