"""Test the token matcher."""
from lint381.linter import SourceCode
from lint381.matcher import (
    match_regex,
    match_tokens,
    match_type,
    with_matched_tokens,
)
from lint381.tokenizer import Token, tokenize


def test_match_regex():
    """Ensure that the regex matcher matches tokens correctly."""
    token = Token(type="identifier", value="foo", start=None, end=None)
    assert match_regex("^foo$")(token)
    assert not match_regex("^bar$")(token)


def test_match_type():
    """Ensure that we match on identifier types."""
    token = Token(type="identifier", value=None, start=None, end=None)
    assert match_type("identifier")(token)
    assert not match_type("binary_operator")(token)


def test_match_tokens():
    """Ensure that we match tokens correctly."""
    code = """
foo qux bar
foo grault bar
foo bar
"""

    expected = [["foo", "qux", "bar"],
                ["foo", "grault", "bar"],
                ["foo", "bar"]]
    assert expected == [
        [token.value for token in match]
        for match in match_tokens(tokenize(code),
                                  start=match_regex("foo"),
                                  end=match_regex("bar"))]


def test_no_matching_token():
    """Ensure that we handle cases when there is no match."""
    code = """
foo
"""

    assert not list(match_tokens(tokenize(code),
                                 start=match_regex("foo"),
                                 end=match_regex("bar")))


def test_match_length():
    """Ensure that we correctly find sequences of a provided length."""
    code = """
foo foo bar
"""
    result = match_tokens(tokenize(code),
                          start=match_regex("foo"),
                          end=match_regex("bar"),
                          length=3)
    result = list(result)
    assert len(result) == 1
    assert [i.value for i in result[0]] == ["foo", "foo", "bar"]


def test_not_enough_lookahead():
    """Ensure that we don't return a match if there's not enough lookahead."""
    code = """
foo bar
"""

    assert not list(match_tokens(tokenize(code),
                                 start=match_regex("foo"),
                                 end=match_regex("bar"),
                                 lookahead=1))


def test_with_matching_tokens():
    """Ensure that we can use the decorator to match tokens."""
    code = """
foo bar
"""

    @with_matched_tokens(start=match_regex("foo"),
                         end=match_regex("bar"))
    def func(source, *, match):
        yield "baz"

    source_code = SourceCode(filename="foo.cpp",
                             tokens=tokenize(code))
    assert list(func(source_code)) == ["baz"]
