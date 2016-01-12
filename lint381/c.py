"""C linters."""
from .code import with_matched_tokens
from .linter import Linter

linter = Linter()


@linter.register
@with_matched_tokens("#define <macro>")
def underscore_define(window, match):
    """Flag #defines that start with underscores."""
    macro = match["macro"]
    if macro.startswith("_"):
        return ("Macro '{}' should not start with an underscore"
                .format(macro))


@linter.register
@with_matched_tokens("struct <struct>")
def struct_capitalized(window, match):
    """Flag structs that don't have capitalized names."""
    struct_name = match["struct"]
    if struct_name[0].islower():
        return ("Struct name '{}' should be capitalized"
                .format(struct_name))
