"""Tools for matching code patterns."""
import collections
import functools
import re


class Position(collections.namedtuple("Position", [
    "row",
    "column",
])):
    """A position of a token.

    :ivar int row: The row of the position. 0-indexed.
    :ivar int column: The column of the position. 0-indexed.
    """

    @property
    def line_display(self):
        """Return the position as a line/column number.

        :returns str: The description of the position.
        """
        return "line {line}, column {column}".format(
            line=self.row + 1,
            column=self.column + 1,
        )

Token = collections.namedtuple("Token", [
    "value",
    "start",
    "end",
])
"""A token in the source file.

:ivar str value: The string value of the token.
:ivar Position start: The start of the token.
:ivar Position end: The end of the token.
"""


def tokenize(string):
    """Tokenize a string.

    :returns list: A list of tokens in the string.
    """
    return list(_Tokenizer(string).tokenize())


class _Tokenizer:
    """Tokenize C/C++ code.

    Note that tokenizing C++ is really hard. This doesn't even try to be good
    at it.
    """

    _TOKEN_PATTERNS = [
        # Number.
        r"""
        [0-9]+

        # Optional decimal point.
        (\.?[0-9]*)
        """,

        # Identifier.
        r"""
        # Possibly a preprocessor directive.
        [#]?

        [_a-zA-Z][_a-zA-Z0-9]+
        """,

        # Single-line comment.
        r"""
        //.+
        """,

        # Multi-character operators.
        r"""
        (
            :: |
            \+\+ | -- |
            == | != | >= | <= |
            && | \|\| |
            \+= | -= | \*= | /= | %= |
            <<= | >>= | &= | \|= | \^=
            << | >> |
        )"""

        # Single-character tokens.
        r"""
        [
            ( )
            \[ \]
            { }
            < >
            ! ~
            + \- * / ^ % & | =
            '
            ; , .
            ? :
        ]
        """
    ]
    _TOKEN_PATTERNS = [re.compile(i, re.VERBOSE)
                       for i in _TOKEN_PATTERNS]

    def __init__(self, string):
        """Tokenize the provided code."""
        # Add a dummy whitespace character to end the last token.
        self._string = string + "\n"
        self._cursor = 0

        self._row = 0
        self._column = 0

    def _char(self):
        """Get the character under the cursor.

        :returns str: The current character.
        """
        assert self._cursor >= 0
        return self._string[self._cursor]

    def _advance_cursor(self):
        """Advance the cursor by one character."""
        if self._char() == "\n":
            self._row += 1
            self._column = 0
        else:
            self._column += 1

        self._cursor += 1

    def _position(self):
        """Get the position of the cursor.

        :return Position: The position of the cursor.
        """
        assert 0 <= self._row < len(self._string)
        assert 0 <= self._column < len(self._string)
        return Position(row=self._row, column=self._column)

    def tokenize(self):
        """Tokenize the provided string.

        This assumes that the string is valid code.

        :returns list: A list of tokens in the string.
        """
        while self._consume_whitespace():
            token = self._get_next_token()
            yield token
            self._advance_cursor()

    def _get_next_token(self):
        """Get the next token from the input string.

        This should leave the cursor at the last character of the returned
        token.

        :returns Token: The next token in the input.
        """
        # Special cases that we need to handle with higher priority or aren't
        # easily handled by regexes.
        special_consumers = [self._consume_string,
                             self._consume_multiline_comment]
        for func in special_consumers:
            token = func()
            if token:
                return token

        token_values = [self._match_pattern(pattern)
                        for pattern in self._TOKEN_PATTERNS]
        token_values = [i for i in token_values if i]
        if not token_values:
            raise ValueError("Couldn't parse token at {}"
                             .format(self._position().line_display))

        # Maximal munch -- pick the longest token.
        token_values.sort(key=len, reverse=True)
        value = token_values[0]

        start_position = self._position()
        # Leave our cursor at the value at the end of the token.
        for _ in range(len(value) - 1):
            self._advance_cursor()
        end_position = self._position()
        return Token(value=value,
                     start=start_position,
                     end=end_position)

    def _match_pattern(self, pattern):
        """If the pattern appears at the beginning of the stream, return it.

        :param pattern: The compiled regex.
        :returns str: The matched pattern, or `None` if there was no
            such token.
        """
        match = pattern.match(self._string[self._cursor:])
        if match:
            return match.group()
        else:
            return None

    def _consume_whitespace(self):
        """Remove whitespace from the beginning of the stream.

        :returns bool: Whether there is anything else left in the stream.
        """
        while self._cursor < len(self._string):
            if self._char().isspace():
                self._advance_cursor()
            else:
                return True
        return False

    def _consume_string(self):
        """Get a string literal from the stream, if possible.

        :returns Token: The string token, or `None` if there was no string at
            the current position.
        :raises ValueError: There was an unterminated string literal.
        """
        if self._char() != '"':
            return None

        start_index = self._cursor
        start_position = self._position()

        # Skip the current quotation mark.
        self._advance_cursor()

        while self._cursor < len(self._string):
            if self._char() == "\\":
                # Ignore backslash escape sequences.
                self._advance_cursor()
            elif self._char() == '"':
                end_index = self._cursor
                end_position = self._position()
                break
            self._advance_cursor()
        else:
            raise ValueError("Unterminated string literal at {}"
                             .format(self._position().line_display))

        return Token(value=self._string[start_index:end_index + 1],
                     start=start_position,
                     end=end_position)

    def _consume_multiline_comment(self):
        """Get a multiline comment from the stream, if possible.

        :returns Token: The multiline comment, or `None` if there was no
            multiline comment at the current position.
        :raises ValueError: There was an unterminated multiline comment.
        """
        def peek_two():
            # Note that this may result in only one character at the end of the
            # stream, which is fine.
            return self._string[self._cursor:self._cursor + 2]

        if peek_two() != "/*":
            return None

        start_position = self._position()
        start_index = self._cursor

        while self._cursor < len(self._string):
            if peek_two() == "*/":
                # Move cursor to the "/".
                self._advance_cursor()

                end_index = self._cursor
                end_position = self._position()
                break
            self._advance_cursor()
        else:
            raise ValueError("Unterminated multiline comment at {}"
                             .format(self._position().line_display))

        return Token(value=self._string[start_index:end_index + 1],
                     start=start_position,
                     end=end_position)


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

        :param Token token: The token.
        :param str pattern: The start or end pattern.
        :returns bool: Whether or not the token matches.
        """
        return re.match(pattern, token.value) is not None
