"""Test the token matcher."""
from lint381.matcher import match_tokens, with_matched_tokens
from lint381.tokenizer import tokenize


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
                                  start="foo",
                                  end="bar")]


def test_no_matching_token():
    """Ensure that we handle cases when there is no match."""
    code = """
foo
"""

    assert not list(match_tokens(tokenize(code), start="foo", end="bar"))


def test_not_enough_lookahead():
    """Ensure that we don't return a match if there's not enough lookahead."""
    code = """
foo bar
"""

    assert not list(match_tokens(tokenize(code),
                                 start="foo",
                                 end="bar",
                                 lookahead=1))


def test_with_matching_tokens():
    """Ensure that we can use the decorator to match tokens."""
    code = """
foo bar
"""

    @with_matched_tokens(start="foo", end="bar")
    def func(tokens, match):
        return "baz"

    assert list(func(tokenize(code))) == ["baz"]
