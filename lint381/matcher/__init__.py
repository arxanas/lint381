"""Basic tools to locally parse parts of the token stream."""
import functools
import re


def match_tokens(tokens, *, start, end=None, lookahead=0, length=None):
    r"""Try to find a pattern marked by `start` and `end` in the token list.

    `start` and `end` are functions provided by the caller to specify if a
    token could be the start or end of a subsequence. For example, consider
    `start` and `end` defined as follows:

        def start(token):
            return token.value == "("

        def end(token):
            return token.value == ")"

    We could use these to return a sequence of tokens including and in between
    a set of parentheses.

    `start` and `end` try to find the tightest set of matched tokens. Thus it
    would match this:

        ( foo + bar ( ) )
                    ^^^

    and not this:

        ( foo + bar ( ) )
        ^^^^^^^^^^^^^^^

    which is typically the better behavior to have.

    For convenience, helper functions such as `match_regex` are defined in this
    module so that you don't have to make your own `start` and `end` functions.
    Rather than define `start` and `end` as above, you could equivalently do
    this:

        match_tokens(tokens,
                     start=match_regex(r"^\($"),
                     end=match_regex(r"^\)$"))

    You can additionally specify a `lookahead` value to return extra tokens
    after the last matched token, or a `length` to specify that you only want
    matches with a specific number of tokens.

    :param list tokens: A sequence of tokens to find matches in.
    :param callable start: The function to match a starting token value
        against. The token is matched if `start` returns `True` when applied to
        it.
    :param callable end: Optional. The function to match an ending token value
        against. The token is matched if `end` returns `True` when applied to
        it. If not provided, only the single token matched by `start` will be
        returned.
    :param int lookahead: A number of extra tokens after the ending token to
        return. If there is a match, but there aren't enough additional
        lookahead tokens to return, no match is yielded.
    :param int length: The number of tokens to match, exactly.
    :yields list: A subsequence of matched tokens.
    """
    if end is None:
        end = start

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

                end_index = j + lookahead
                if end(end_token) and end_index < len(tokens):
                    yield tokens[i:end_index + 1]
            else:
                # Scan ahead for the matching end token.
                for j, end_token in enumerate(tokens[i:], i):
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


class with_matched_tokens:
    """Decorator for a linter function that automatically runs `match_tokens`.

    Since nearly all linting functions run `match_tokens`, it makes sense to
    provide an easy way to do it.

    This decorator modifies the function to be called on each match, rather
    than just once with the token stream. The match is passed as a keyword
    argument to the linting function.

    So this:

        @linter.register
        def flag_something(source):
            for match in match_tokens(source.tokens,
                                      start=foo,
                                      end=bar):
                ...

    becomes this:

        @linter.register
        @with_matched_tokens(start=foo, end=bar, ...)
        def flag_something(source, *, match):
            ...
    """

    def __init__(self, **kwargs):
        """Initialize the decorator with the arguments to `match_tokens`.

        :param dict kwargs: The keyword arguments to pass to `match_tokens`.
        """
        self._kwargs = kwargs

    def __call__(self, func):
        """Wrap the function so that it is called with each match.

        The matched tokens are available in the `match` keyword argument.

        :param function func: The linter function to wrap.
        :returns function: The wrapped function.
        """
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            source = args[0]
            for match in match_tokens(source.tokens, **self._kwargs):
                kwargs["match"] = match
                yield from func(*args, **kwargs)
        return wrapped
