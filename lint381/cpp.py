"""C++ linters."""
import re

from lint381 import c
from .linter import Error, Linter
from .matcher import match_regex, match_type, with_matched_tokens

linter = Linter()

_IMPORTED_C_LINTERS = [
    "prohibited_types",
    "underscore_define",
    "uppercase_define",
    "typename_capitalized",
    "string_constant_array",
]
for linter_func in _IMPORTED_C_LINTERS:
    linter.register(getattr(c, linter_func))


@linter.register
@with_matched_tokens(start=match_type("comment"))
def triple_asterisk_comment(tokens, *, match):
    """Flag instruction comments, which have three asterisks."""
    if "***" in match[0].value:
        yield Error(message="Remove triple-asterisk comments", tokens=match)


_DEPRECATED_TOKEN_SUGGESTIONS = {
    "NULL": "nullptr",
    "malloc": "new",
    "free": "delete",
    "typedef": "using",
    "scanf": "cin",
    "printf": "cout",
}
"""Tokens that are deprecated in C++ and their replacements."""

_DEPRECATED_TOKEN_REGEX = "^{}$".format(
    "|".join(re.escape(i) for i in _DEPRECATED_TOKEN_SUGGESTIONS)
)
"""Matches a deprecated token."""


@linter.register
@with_matched_tokens(start=match_regex(_DEPRECATED_TOKEN_REGEX))
def deprecated_tokens(tokens, *, match):
    """Suggest alternatives to deprecated tokens such as `NULL`."""
    bad_token = match[0].value
    suggestion = _DEPRECATED_TOKEN_SUGGESTIONS[bad_token]
    yield Error(message="Use '{}' in C++ code, not '{}'"
                        .format(suggestion, bad_token),
                tokens=match)


@linter.register
@with_matched_tokens(start=match_regex("^memset|memmove|memcpy|exit$"))
def prohibited_functions(tokens, *, match):
    """Flag prohibited functions."""
    yield Error(message="Don't use '{}'".format(match[0].value),
                tokens=match)


@linter.register
@with_matched_tokens(start=match_regex("^using$"), end=match_regex("^;$"))
def alias_containers_not_iterators(tokens, *, match):
    """Flag type-aliasing an iterator instead of its container.

    For example, flag this code:

        using Foo_t = std::vector<int>::iterator;

    Because it should be this:

        using Foo_t = std::vector<int>;
        // ...
        Foo_t::iterator bar = /* ... */
    """
    iterator = match[-2].value

    # Lowercase it because there are `Iterator` and `const_Iterator`s in this
    # class.
    if iterator.lower() not in ["iterator", "const_iterator"]:
        return

    yield Error(message="Create type aliases for containers, not iterators",
                tokens=match[-3:-1])


@linter.register
@with_matched_tokens(start=match_regex("^#define$"))
def use_const_not_define(tokens, *, match):
    """Flag using `#define` to declare constants in C++."""
    define_token = match[0]
    tokens_on_line = [i for i in tokens
                      if i.start.row == define_token.start.row
                      if i.end.row == define_token.end.row]

    # This isn't a const declaration.
    if len(tokens_on_line) <= 2:
        return

    # If there's an open-paren immediately after the `#define`d name, this is a
    # macro definition.
    constant_token = tokens_on_line[1]
    open_paren = tokens_on_line[2]
    macro_start = constant_token.end.column + 1
    if open_paren.value == "(" and open_paren.start.column == macro_start:
        return

    constant_name = constant_token.value
    yield Error(message="Use 'const' or 'constexpr' to create constant '{}', "
                        "not '#define'"
                        .format(constant_name),
                tokens=tokens_on_line)


@linter.register
@with_matched_tokens(start=match_regex("^template$"),
                     end=match_regex("^class$"))
def use_typename_over_class(tokens, *, match):
    """Flag using class in template parameters."""
    # Three tokens: "template < class"
    if len(match) != 3:
        return

    template_var_type = match[-1]
    yield Error(message="Use 'typename' instead of 'class' "
                        "for template parameters",
                tokens=[template_var_type])


@linter.register
@with_matched_tokens(start=match_regex("^while$"), end=match_regex(r"^\)$"))
def loop_condition_boolean(tokens, *, match):
    """Flag using a literal `0` or `1` in a loop condition.

    Instead use `true` or `false`.
    """
    # Four tokens: "while ( 1 )"
    if len(match) != 4:
        return

    condition = match[2].value
    suggestion = {
        "0": "false",
        "1": "true",
    }[condition]

    yield Error(message="Use '{}' instead of '{}' in loop condition"
                        .format(suggestion, condition),
                tokens=match[1:])
