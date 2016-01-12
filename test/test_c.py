"""Test the C linters."""
from lint381.c import linter


def assert_has_error(line, error_message):
    """Assert that the given line of source code has an error.

    :param str line: The line of source code.
    :param str error_message: The expected error message.
    """
    lines = [line]
    assert linter.lint(lines) == {0: [error_message]}


def assert_no_error(line):
    """Assert that the given line of source code doesn't have an error.

    :param str line: The line of source code.
    """
    lines = [line]
    assert not linter.lint(lines)


def test_correct_source_code():
    """Ensure that correct source code doesn't raise errors."""
    code = """
    int main() {
        return 0
    }
    """
    lines = code.strip().splitlines()
    assert not linter.lint(lines)


def test_macro_underscore():
    """Ensure that macros don't start with underscores."""
    assert_has_error("#define __FOO__",
                     "Macro `__FOO__` should not start with an underscore")
    assert_no_error("#define BAR")
