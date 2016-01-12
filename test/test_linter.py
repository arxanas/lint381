"""Test the linter tools."""
from lint381.linter import Linter


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

    assert list(linter.lint("code")) == [
        "foo",
        "bar",
    ]
