"""Test the code-manipulation functions."""
import pytest

from lint381.tokenizer import Position, Token, tokenize


def test_tokenize():
    """Ensure that we tokenize code correctly."""
    assert tokenize("""
int main() {

}
foo ();
""".strip()) == [
        Token(start=Position(row=0, column=0),
              end=Position(row=0, column=2),
              value="int"),
        Token(start=Position(row=0, column=4),
              end=Position(row=0, column=7),
              value="main"),
        Token(start=Position(row=0, column=8),
              end=Position(row=0, column=8),
              value="("),
        Token(start=Position(row=0, column=9),
              end=Position(row=0, column=9),
              value=")"),
        Token(start=Position(row=0, column=11),
              end=Position(row=0, column=11),
              value="{"),
        Token(start=Position(row=2, column=0),
              end=Position(row=2, column=0),
              value="}"),

        Token(start=Position(row=3, column=0),
              end=Position(row=3, column=2),
              value="foo"),
        Token(start=Position(row=3, column=4),
              end=Position(row=3, column=4),
              value="("),
        Token(start=Position(row=3, column=5),
              end=Position(row=3, column=5),
              value=")"),
        Token(start=Position(row=3, column=6),
              end=Position(row=3, column=6),
              value=";"),
    ]


def test_tokenize_string():
    """Ensure that we tokenize strings correctly."""
    assert tokenize("""
hello = "foo"
;
""".strip()) == [
        Token(value="hello",
              start=Position(row=0, column=0),
              end=Position(row=0, column=4)),
        Token(value="=",
              start=Position(row=0, column=6),
              end=Position(row=0, column=6)),
        Token(value='"foo"',
              start=Position(row=0, column=8),
              end=Position(row=0, column=12)),
        Token(value=";",
              start=Position(row=1, column=0),
              end=Position(row=1, column=0)),
    ]


def test_fail_to_parse_token():
    """Ensure that we reject code with unknown tokens."""
    with pytest.raises(ValueError):
        tokenize(r"`")


def test_tokenize_binary_operator():
    """Ensure that binary operators don't have surrounding whitespace.

    Regression test.
    """
    code = "foo == bar"
    assert [i.value for i in tokenize(code)] == ["foo", "==", "bar"]


def test_tokenize_unterminated_string_literal():
    """Ensure that we reject unterminated string literals."""
    with pytest.raises(ValueError):
        tokenize(r"""
        "foo
        """)


def test_tokenize_backslash_string_literal():
    """Ensure that we handle backslash-escapes correctly in strings."""
    code = r"""
"foo\"bar\\baz"
""".strip()

    assert tokenize(code) == [
        Token(value=code,
              start=Position(row=0, column=0),
              end=Position(row=0, column=14)),
    ]


def test_tokenize_single_line_comment():
    """Ensure that we tokenize single-line comments correctly."""
    assert tokenize(r"""
struct foo;
// this is a comment with bad code: struct foo;
""".strip()) == [
        Token(value="struct",
              start=Position(row=0, column=0),
              end=Position(row=0, column=5)),
        Token(value="foo",
              start=Position(row=0, column=7),
              end=Position(row=0, column=9)),
        Token(value=";",
              start=Position(row=0, column=10),
              end=Position(row=0, column=10)),
        Token(value="// this is a comment with bad code: struct foo;",
              start=Position(row=1, column=0),
              end=Position(row=1, column=46)),
    ]


def test_tokenize_multiline_comment():
    """Ensure that we tokenize multiline comments."""
    assert tokenize(r"""
foo
/* bar
baz */
""".strip()) == [
        Token(value="foo",
              start=Position(row=0, column=0),
              end=Position(row=0, column=2)),
        Token(value="/* bar\nbaz */",
              start=Position(row=1, column=0),
              end=Position(row=2, column=5)),
    ]


def test_tokenize_unterminated_multiline_comment():
    """Ensure that we reject unterminated multiline comments."""
    with pytest.raises(ValueError):
        tokenize("/*")
