"""Linter tools."""
import collections

from .code import tokenize


class Window(collections.namedtuple("Window", ["lines", "line_num"])):
    """A window onto a segment of the source code.

    :ivar list lines: The list of lines in the file.
    :ivar int line_num: The line number we're currently looking at.
    """

    @property
    def line(self):
        """The line we're currently looking at."""
        return self.lines[self.line_num]

    @property
    def tokens(self):
        """The tokens in the current line."""
        return tokenize(self.line)


class Linter:
    """A registry of linters for a specific language."""

    def __init__(self):
        """Initialize the linter registry to be empty."""
        self._linters = []

    def register(self, func):
        """Register the provided function as a linter.

        This should be used as a decorator:

        ```
        linters = Linter()

        @linters.register
        def linter():
            ...
        ```

        :param function func: The linting function.
        """
        self._linters.append(func)
        return func

    def lint(self, lines):
        """Find linting errors on the specified lines of source code."""
        errors = collections.defaultdict(list)

        for line_num, _ in enumerate(lines):
            window = Window(lines=lines, line_num=line_num)
            for func in self._linters:
                error_message = func(window)
                if error_message:
                    errors[line_num].append(error_message)

        return errors
