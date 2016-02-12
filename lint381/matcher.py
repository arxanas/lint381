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
                yield from func(*args, **kwargs)
        return wrapped


def match_tokens(tokens, *, start, end=None, lookahead=0, length=None):
    """Find the specified pattern in the tokens.

    :param list tokens: A sequence of tokens to find matches in.
    :param str start: The starting pattern to match a token value against.
    :param str end: The ending pattern to match a token value against.
    :param int lookahead: The number of extra tokens after the ending token to
        return.
    :param int length: The number of tokens to match, exactly.
    :yields list: A subsequence of matched tokens.
    """
    if end is None:
        end = start

    if length is not None:
        assert length > 0
        assert not lookahead, "Lookahead not implemented for length != 0"

    i = 0
    while i < len(tokens):
        start_token = tokens[i]
        if start(start_token):
            # Quick path in case we know the exact length we want.
            if length is not None:
                # Subtract one because we want an inclusive interval.
                j = i + length - 1

                try:
                    end_token = tokens[j]
                except IndexError:
                    # We indexed out of bounds, so we can't possibly find a
                    # match of the specified length anymore.
                    break

                if end(end_token):
                    yield tokens[i:j + 1]
            else:
                # Scan ahead for the matching end token.
                for j in range(i, len(tokens)):
                    end_token = tokens[j]

                    # If we find a better starting point, use that instead.
                    # This minimizes the distance between the start and the end
                    # token.
                    if start(end_token):
                        start_token = end_token
                        i = j

                    if end(end_token):
                        # If we can't provide enough lookahead, don't yield the
                        # match at all.
                        j += lookahead
                        if j < len(tokens):
                            yield tokens[i:j + 1]

                        # Skip forward to this token.
                        i = j
                        break
        i += 1


def match_regex(regex):
    """Return a matcher that matches on the token's value.

    :param str regex: The regex to match the token value against.
    :returns function: The matcher.
    """
    def matcher(token):
        return re.match(regex, token.value) is not None
    return matcher


def match_type(type):
    """Return a matcher that matches on the token's type.

    :param str type: The token type.
    :returns function: The matcher.
    """
    def matcher(token):
        return token.type == type
    return matcher
