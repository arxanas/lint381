"""C linters."""
from .code import match_tokens
from .linter import Error, Linter

linter = Linter()


@linter.register
@match_tokens(start="#define", lookahead=1)
def underscore_define(tokens, match):
    """Flag #defines that start with underscores."""
    macro = match[1].value
    if macro.startswith("_"):
        return Error(message="Macro '{}' should not start with an underscore"
                             .format(macro),
                     tokens=match)


@linter.register
@match_tokens(start="struct", end="({|;)")
def struct_capitalized(tokens, match):
    """Flag structs that don't have capitalized names."""
    struct_name = match[1].value
    if struct_name[0].islower():
        return Error(message="Struct name '{}' should be capitalized"
                     .format(struct_name),
                     tokens=match)
