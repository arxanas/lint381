"""Test the C linters."""
from lint381.c import linter


def assert_has_error(code, error_message):
    """Assert that the given source code has an error.

    :param str code: The source code.
    :param str error_message: The expected error message.
    """
    assert error_message in [i.message for i in linter.lint(code)]


def assert_no_error(code):
    """Assert that the given source code doesn't have an error.

    :param str code: The source code.
    """
    assert not list(linter.lint(code))


def test_correct_source_code():
    """Ensure that correct source code doesn't raise errors."""
    code = """
    int main() {
        return 0
    }
    """
    assert not list(linter.lint(code.strip()))


def test_macro_underscore():
    """Ensure that macros don't start with underscores."""
    assert_has_error("#define __FOO__",
                     "Macro '__FOO__' should not start with an underscore")
    assert_no_error("#define BAR")


def test_struct_capitalized():
    """Ensure that struct names must be capitalized."""
    assert_has_error("struct foo;",
                     "Struct name 'foo' should be capitalized")
    assert_no_error("struct Foo;")
