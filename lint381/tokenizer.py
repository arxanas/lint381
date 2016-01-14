"""Tools for matching code patterns."""
import collections
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
    "type",
    "value",
    "start",
    "end",
])
"""A token in the source file.

:ivar str type: The type of the token, such as "identifier".
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
        ("number", r"""
        [0-9]+

        # Optional decimal point.
        (\.?[0-9]*)
        """),

        ("keyword", r"""
        (
            auto |
            break |
            case |
            char |
            const |
            continue |
            default |
            do |
            double |
            else |
            enum |
            extern |
            float |
            for |
            goto |
            if |
            int |
            long |
            register |
            return |
            short |
            signed |
            sizeof |
            static |
            struct |
            switch |
            typedef |
            union |
            unsigned |
            void |
            volatile |
            while
        )"""),

        ("identifier", r"""
        # Possibly a preprocessor directive.
        [#]?

        [_a-zA-Z]([_a-zA-Z0-9]+)?
        """),

        ("comment", r"""
        //.+
        """),

        ("unary_operator", r"""
        (
            \+\+ | -- | ! | ~
        )
        """),

        # Two-character operators.
        ("binary_operator", r"""
        (
            # Relational.
            ==  | != | <= | >=

            # Arithmetic.
            \+= | -= | \*= | /= | %= |

            # Logical.
            &&  | \|\| |

            # Bitwise.
            <<= | >>= | &= | \|= | \^= |
            <<  | >>  |
        )
        """),

        # One-character operators.
        ("binary_operator", r"""
        [
            + \- * / %
            ^ & |
            < >
            =
        ]
        """),

        ("grouping", r"""
        (
            \( | \) |
            \[ | \] |
            \{ | \} |
            ::      |
            ,  | ;  |
            \.      |
            \? | :
        )
        """),
    ]
    _TOKEN_PATTERNS = [(group, re.compile(pattern, re.VERBOSE))
                       for group, pattern in _TOKEN_PATTERNS]

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

        token_values = [(group, self._match_pattern(pattern))
                        for group, pattern in self._TOKEN_PATTERNS]
        token_values = [(group, value)
                        for group, value in token_values
                        if value]
        if not token_values:
            raise ValueError("Couldn't parse token at {}"
                             .format(self._position().line_display))

        # Maximal munch -- pick the longest token.
        token_values.sort(key=lambda i: len(i[1]),
                          reverse=True)
        group, value = token_values[0]

        start_position = self._position()
        # Leave our cursor at the value at the end of the token.
        for _ in range(len(value) - 1):
            self._advance_cursor()
        end_position = self._position()
        return Token(type=group,
                     value=value,
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
        if self._char() == '"':
            quote = '"'
        elif self._char() == "'":
            quote = "'"
        else:
            return None

        start_index = self._cursor
        start_position = self._position()

        # Skip the current quotation mark.
        self._advance_cursor()

        while self._cursor < len(self._string):
            if self._char() == "\\":
                # Ignore backslash escape sequences.
                self._advance_cursor()
            elif self._char() == quote:
                end_index = self._cursor
                end_position = self._position()
                break
            self._advance_cursor()
        else:
            raise ValueError("Unterminated string literal at {}"
                             .format(self._position().line_display))

        return Token(type="string",
                     value=self._string[start_index:end_index + 1],
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

        return Token(type="comment",
                     value=self._string[start_index:end_index + 1],
                     start=start_position,
                     end=end_position)
