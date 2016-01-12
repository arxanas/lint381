"""Test the linter tools."""
from lint381.linter import Linter


def test_linter():
    """Ensure that the linter registers and applies all linting functions."""
    linter = Linter()

    @linter.register
    def foo(window):
        if window.line_num == 0:
            return "foo"

    @linter.register
    def bar(window):
        return "bar"

    assert linter.lint(["foo", "bar"]) == {
        0: ["foo", "bar"],
        1: ["bar"],
    }
