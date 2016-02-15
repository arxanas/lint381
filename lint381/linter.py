"""Defines a linter for a given language.

Each language should declare a linter and then register linting functions:

    linter = Linter()

    @linter.register
    def flag_something(tokens):
        if foo(tokens):
            yield Error(...)

Then a client can call `linter.lint` on their source code to get a list of
linting errors.
"""
import collections

from .tokenizer import tokenize


class SourceCode(collections.namedtuple("SourceCode", ["filename", "tokens"])):
    """The tokenized source code of a file.

    :ivar str filename: The name of the source file.
    :ivar list tokens: The list of tokens in the file.
    """

    @property
    def is_header_file(self):
        """Whether or not this file is a header file."""
        return self.filename.endswith(".h")


Error = collections.namedtuple("Error", [
    "message",
    "tokens",
])
"""A linter error.

:ivar str message: The linting error to display to the user.
:ivar list tokens: The list of tokens that caused the linting error, in the
    order that they appear in the source code. (This should be a contiguous
    subsequence of the list of tokens.) This is used to determine the
    line/column number, and to underline tokens.
"""


class Linter:
    """Lints source code and produces errors.

    The linter requires that functions be registered with the linter. Each such
    function should take a list of tokens and yield any number of `Error`s.
    For example:

        @linter.register
        def complain(tokens):
            for i in tokens:
                if i.value == "foo":
                    yield Error(message="foo not allowed",
                                tokens=[i])

    :ivar list linters: The list of linting functions associated with this
        linter.
    """

    def __init__(self):
        """Initialize the linter with no linting functions."""
        self.linters = []

    def register(self, func):
        """Register the provided function as a linter.

        This should be used as a decorator:

            linter = Linter()

            @linter.register
            def linter():
                ...

        :param function func: The linting function.
        :returns function: The same function, unchanged.
        """
        self.linters.append(func)
        return func

    def lint(self, filename, code):
        """Find linting errors on the specified source code.

        :param str code: The source code as a string.
        :param str filename: The name of the source file.
        :returns list: A list of `Error`s in the source code.
        """
        errors = []

        source_code = SourceCode(filename=filename,
                                 tokens=tokenize(code))
        for func in self.linters:
            errors.extend(func(source_code))

        return errors
