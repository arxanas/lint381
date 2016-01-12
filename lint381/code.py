"""Tools for matching code patterns."""


def tokenize(string):
    """Split a string into tokens.

    Note that tokenizing C++ is really hard. This doesn't even try to be good
    at it.

    TODO: Tokenize strings and comments correctly.

    :param str string: The string to tokenize. This could be a line or a file.
    :returns list: A list of tokens, each of which is a string.
    """
    return string.strip().split()


def match_tokens(window, pattern):
    """Match a pattern of tokens on the current window.

    :param lint381.linter.Window window: The window onto the source code.
    :param str pattern: The pattern to match. TODO: Provide example.
    :returns dict: A dictionary of the matched pattern values, or `None` if
        there was no match.
    """
    search_tokens = pattern.split()

    def ngrams(seq, n):
        parts = []
        for i in range(n):
            parts.append(seq[i:])
        return zip(*parts)

    def match_local(sequence):
        variables = {}
        for variable, token in zip(search_tokens, candidate):
            # TODO: Might not be able to use < and > because of template
            # parameters.
            if variable.startswith("<") and variable.endswith(">"):
                variable = variable[1:-1]
                variables[variable] = token
            else:
                if variable != token:
                    return None
        return variables

    for candidate in ngrams(window.tokens, n=len(search_tokens)):
        match = match_local(candidate)
        if match:
            return match
    return None
