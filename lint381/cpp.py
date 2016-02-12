"""C++ linters."""
from lint381 import c
from .linter import Error, Linter
from .matcher import match_regex, match_type, with_matched_tokens

linter = Linter()

_IMPORTED_C_LINTERS = [
    "prohibited_types",
    "underscore_define",
    "uppercase_define",
    "typename_capitalized",
]
for linter_func in _IMPORTED_C_LINTERS:
    linter.register(getattr(c, linter_func))


@linter.register
@with_matched_tokens(start=match_type("comment"))
def triple_asterisk_comment(tokens, *, match):
    """Flag instruction comments, which have three asterisks."""
    if "***" in match[0].value:
        yield Error(message="Remove triple-asterisk comments", tokens=match)


@linter.register
@with_matched_tokens(start=match_regex("^NULL|malloc|free|typedef$"))
def prohibited_tokens(tokens, *, match):
    """Flag usage of NULL, malloc, and free."""
    bad_token = match[0].value
    suggestion = {
        "NULL": "nullptr",
        "malloc": "new",
        "free": "delete",
        "typedef": "using",
    }[bad_token]
    yield Error(message="Use {} in C++ code, not {}"
                        .format(suggestion, bad_token),
                tokens=match)
