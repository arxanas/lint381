"""Tools for matching code patterns."""
import collections
import functools
import re


Position = collections.namedtuple("Position", [
    "row",
    "column",
])
"""A position of a token.

:ivar int row: The row of the position. 0-indexed.
:ivar int column: The column of the position. 0-indexed.
"""

Token = collections.namedtuple("Token", [
    "value",
    "start",
    "end",
])
"""A token in the source file.

:ivar str value: The string value of the token.
:ivar lint381.code.Position start: The start of the token.
:ivar lint381.code.Position end: The end of the token.
"""


def tokenize(string):
    """Split a string into tokens.

    This assumes that the string is valid code.

    Note that tokenizing C++ is really hard. This doesn't even try to be good
    at it.

    TODO: Tokenize strings and comments correctly.

    :param str string: The string to tokenize. This could be a line or a file.
    :returns list: A list of `lint381.code.Token`s.
    """
    end_tokens = ["(", ")", "[", "]", "{", "}", ";"]
    row = 0
    column = 0

    tokens = []
    token_start = None
    token_start_index = None
    for i, c in enumerate(string):
        if c == "\n":
            row += 1
            column = 0

        def get_next_char():
            if i == len(string) - 1:
                # Pretend there's a word-breaking next token.
                return " "
            else:
                return string[i + 1]
        next_char = get_next_char()

        def get_token_value():
            return string[token_start_index:i + 1]

        def start_token():
            nonlocal token_start
            nonlocal token_start_index
            token_start = Position(row, column)
            token_start_index = i

        def end_token():
            nonlocal token_start
            nonlocal token_start_index
            token_end = Position(row, column)
            tokens.append(Token(start=token_start,
                                end=token_end,
                                value=get_token_value()))
            token_start = None

        if not c.isspace():
            if token_start is None:
                start_token()
            if (get_token_value() in end_tokens or
                    next_char in end_tokens or
                    next_char.isspace()):
                end_token()

        if c != "\n":
            column += 1
    return tokens


class match_tokens:
    """Pass the result of matching tokens to a linter."""

    def __init__(self, *, start, end=None, lookahead=0):
        """Initialize to match a range of tokens.

        :param str start: The starting token. For example, 'enum'.
        :param str end: The ending token. For example, '}'. If not provided,
            assumes that the ending token is the same as the starting token
            (and therefore the result should be only one token).
        :param int lookahead: The number of additional tokens to return beyond
            the last one.
        """
        self._start = start
        if end is not None:
            self._end = end
        else:
            self._end = start
        self._lookahead = lookahead

    def __call__(self, func):
        """Send the matched tokens to the decorated function.

        The tokens are available in the `match` keyword argument.

        :param function func: The linter function to wrap.
        :returns function: The wrapped function.
        """
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            tokens = args[0]
            for match in self._match_tokens(tokens):
                kwargs["match"] = match
                error = func(*args, **kwargs)
                if error:
                    yield error
        return wrapped

    def _match_tokens(self, tokens):
        """Find the specified pattern in the tokens.

        :param list tokens: A sequence of tokens to find matches in.
        :yields list: A subsequence of matched tokens.
        """
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if self._token_matches_pattern(token, self._start):
                # Scan ahead for the matching end token.
                for j, end_token in enumerate(tokens[i:], i):
                    if self._token_matches_pattern(end_token, self._end):
                        # If we can't provide enough lookahead, don't yield the
                        # match at all.
                        j += self._lookahead
                        if j < len(tokens):
                            yield tokens[i:j + 1]
                        i = j
                        break
            i += 1

    def _token_matches_pattern(self, token, pattern):
        """Determine whether a token matches a start/end pattern.

        :param lint381.code.Token token: The token.
        :param str pattern: The start or end pattern.
        :returns bool: Whether or not the token matches.
        """
        return re.match(pattern, token.value) is not None
