"""Test the linter tools."""
from lint381.linter import Linter, SourceCode


def test_linter():
    """Ensure that the linter registers and applies all linting functions."""
    linter = Linter()

    caught_foo = False

    @linter.register
    def foo(tokens):
        nonlocal caught_foo
        if not caught_foo:
            caught_foo = True
            yield "foo"

    @linter.register
    def bar(tokens):
        yield "bar"

    assert list(linter.lint("code.cpp", "code")) == [
        "foo",
        "bar",
    ]


def test_is_header_file():
    """Ensure that we can distinguish header from source files."""
    source = SourceCode(filename="foo.cpp", tokens=[])
    assert not source.is_header_file

    source = SourceCode(filename="foo.h", tokens=[])
    assert source.is_header_file
