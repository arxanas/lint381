"""C++ linters."""
from .c import linter as c_linter
from .linter import Error, Linter
from .matcher import match_type, with_matched_tokens

linter = Linter()

# Import the C linters into the C++ linter.
for lint_func in c_linter.linters:
    linter.register(lint_func)


@linter.register
@with_matched_tokens(start=match_type("comment"))
def triple_asterisk_comment(tokens, *, match):
    """Flag instruction comments, which have three asterisks."""
    if "***" in match[0].value:
        yield Error(message="Remove triple-asterisk comments", tokens=match)
