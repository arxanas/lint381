"""C linters."""
from .code import match_tokens
from .linter import Linter

linter = Linter()


@linter.register
def underscore_define(window):
    """Find #defines that start with underscores."""
    match = match_tokens(window, "#define <macro>")
    if not match:
        return

    macro = match["macro"]
    if macro.startswith("_"):
        return ("Macro `{}` should not start with an underscore"
                .format(macro))
