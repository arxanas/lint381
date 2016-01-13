"""Match parts of the token stream."""
import functools
import re


class with_matched_tokens:
    """Pass the result of matching tokens to a linter."""

    def __init__(self, **kwargs):
        """Initialize to match a range of tokens.

        :param dict kwargs: The keyword arguments to pass to `match_tokens`.
        """
        self._kwargs = kwargs

    def __call__(self, func):
        """Send the matched tokens to the decorated function.

        The tokens are available in the `match` keyword argument.

        :param function func: The linter function to wrap.
        :returns function: The wrapped function.
        """
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            tokens = args[0]
            for match in match_tokens(tokens, **self._kwargs):
                kwargs["match"] = match
                error = func(*args, **kwargs)
                if error:
                    yield error
        return wrapped


def match_tokens(tokens, *, start, end=None, lookahead=0):
    """Find the specified pattern in the tokens.

    :param list tokens: A sequence of tokens to find matches in.
    :param str start: The starting pattern to match a token value against.
    :param str end: The ending pattern to match a token value against.
    :param int lookahead: The number of extra tokens after the ending token to
        return.
    :yields list: A subsequence of matched tokens.
    """
    if end is None:
        end = start

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if _token_matches_pattern(token, start):
            # Scan ahead for the matching end token.
            for j, end_token in enumerate(tokens[i:], i):
                if _token_matches_pattern(end_token, end):
                    # If we can't provide enough lookahead, don't yield the
                    # match at all.
                    j += lookahead
                    if j < len(tokens):
                        yield tokens[i:j + 1]
                    i = j
                    break
        i += 1


def _token_matches_pattern(token, pattern):
    """Determine whether a token matches a start/end pattern.

    :param Token token: The token.
    :param str pattern: The start or end pattern.
    :returns bool: Whether or not the token matches.
    """
    return re.match(pattern, token.value) is not None
