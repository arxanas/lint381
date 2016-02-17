"""C linters."""
from .linter import Error, Linter
from .matcher import (
    match_regex,
    match_tokens,
    match_type,
    with_matched_tokens,
)

linter = Linter()


@linter.register
@with_matched_tokens(start=match_regex("^sizeof$"),
                     end=match_regex("^char$"), lookahead=1)
def sizeof_char(source, *, match):
    """Flag sizeof(char) as it defined to be 1 and is redundant."""
    error_message = "sizeof(char) is redundant as it is defined to be 1"

    if match[1].value == "char" and match[2].value not in ["(", "[", "*"]:
        yield Error(error_message, tokens=[match[0], match[1]])
    elif (match[1].value == "(" and match[2].value == "char" and
            match[3].value == ")"):
        yield Error(error_message, tokens=[match[0], match[1],
                    match[2], match[3]])


@linter.register
@with_matched_tokens(start=match_regex("^(unsigned|float)$"))
def prohibited_types(source, *, match):
    """Flag prohibited numeric types."""
    type = match[0]
    typename = type.value
    yield Error(message="Prohibited type '{}'"
                        .format(typename),
                tokens=[type])


@linter.register
@with_matched_tokens(start=match_regex("^#define$"), lookahead=1)
def underscore_define(source, *, match):
    """Flag #defines that start with underscores."""
    define = match[1]
    macro = define.value
    if macro.startswith("_"):
        yield Error(message="Macro '{}' should not start with an underscore"
                            .format(macro),
                    tokens=[define])


@linter.register
@with_matched_tokens(start=match_regex("^#define$"), lookahead=1)
def uppercase_define(source, *, match):
    """Flag non-uppercase #defines."""
    define = match[1]
    macro = define.value
    if not macro.isupper():
        yield Error(message="Macro '{}' should be uppercase"
                            .format(macro),
                    tokens=[define])


@linter.register
@with_matched_tokens(start=match_regex("^(struct|enum|class)$"),
                     end=match_regex("^({|;)$"))
def typename_capitalized(source, *, match):
    """Flag type names that aren't capitalized."""
    type = match[0].value
    type_name = match[1].value
    if type_name[0].islower():
        yield Error(message="{} name '{}' should be capitalized"
                            .format(type.capitalize(), type_name),
                    tokens=[match[1]])


@linter.register
@with_matched_tokens(start=match_regex("^enum$"),
                     end=match_type("identifier"),
                     length=2)
def enums_end_with_e(source, *, match):
    """Flag enums that don't end with '_e'."""
    enum = match[-1]
    enum_name = enum.value
    if not enum_name.endswith("_e"):
        yield Error(message="Enum '{}' should end with '_e'"
                            .format(enum_name),
                    tokens=[enum])


@linter.register
@with_matched_tokens(start=match_regex("^typedef$"),
                     end=match_regex("^;$"))
def typedefs_end_with_t(source, *, match):
    """Flag typedefs that don't end with '_t'."""
    typedef = match[-2]
    typedef_name = typedef.value

    # Assume it's a function pointer, so don't try to name that.
    if typedef_name == ")":
        return

    # We're inside a construct like `typedef struct { struct Foo_t bar; };`.
    if any(i.value == "{" for i in match):
        return

    if not typedef_name.endswith("_t"):
        yield Error(message="Typedef '{}' should end with '_t'"
                            .format(typedef_name),
                    tokens=[typedef])


@linter.register
@with_matched_tokens(start=match_regex("^(==|!=)$"),
                     end=match_regex("^\)$"))
def comparison_to_null(source, *, match):
    """Flag comparisons to null values."""
    operator = match[0]
    operand = match[1]

    # Ensure that we only match comparisons inside an if-statement or similar.
    next_token = match[2]
    if next_token.value != ")":
        return

    if operator.value in ["==", "!="] and operand.value in [r"'\0'", "NULL"]:
        yield Error(message="Comparison to {} should be avoided"
                            .format(operand.value),
                    tokens=[operator, operand])


@linter.register
@with_matched_tokens(start=match_regex("^enum$"),
                     end=match_regex("^\}$"))
def enum_members_all_caps(source, *, match):
    """Flag enum values that aren't in all-caps."""
    enum_body = list(match_tokens(match,
                                  start=match_regex("^\{$"),
                                  end=match_regex("^\}$")))
    enum_body = enum_body[0]

    for enum_member in match_tokens(enum_body,
                                    start=match_type("identifier"),
                                    end=match_regex("^(,|\})$")):
        enum_member = enum_member[0]
        if not enum_member.value.isupper():
            yield Error(message="Enum member '{}' should be all-caps"
                                .format(enum_member.value),
                        tokens=[enum_member])


@linter.register
@with_matched_tokens(start=match_regex("^\($"),
                     end=match_regex("^malloc$"))
def cast_malloc(source, *, match):
    """Flag casting the result of 'malloc'."""
    # Ensure that the open paren matches with a close paren right before the
    # malloc (i.e. is a cast).
    close_paren = match[-2]
    if close_paren.value != ")":
        return

    yield Error(message="Don't cast the result of 'malloc'",
                tokens=match[:-1])


@linter.register
@with_matched_tokens(start=match_regex("^const$"),
                     end=match_regex("^]$"),
                     length=5)
def string_constant_array(source, *, match):
    """Flag string constants declared as an array instead of a pointer."""
    if match[1].value != "char":
        return

    constant_name = match[2].value
    brackets = match[-2:]
    yield Error(message="Declare '{}' as 'const char* const', "
                        "not 'const char[]'"
                        .format(constant_name),
                tokens=brackets)


@linter.register
def user_includes_before_system_includes(source):
    """Flag putting user includes after a system include.

    That is, this is invalid:

        #include <stdio.h>
        #include "foo.h"

    It should be this:

        #include "foo.h"
        #include <stdio.h>
    """
    includes = _find_includes(source.tokens)
    started_system_includes = False
    for include in includes:
        # For system includes, the next tokens are '<', 'stdio', '.', 'h', '>'.
        # But for a user include, the next token is a single string token.  So
        # we look at the first character of the next token to handle both of
        # these cases.
        include_type = include[1].value[0]
        assert include_type in ["<", '"']

        if include_type == "<":
            started_system_includes = True
        elif include_type == '"' and started_system_includes:
            yield Error(message="User include '{}' should "
                                "be before system includes"
                                .format(include[1].value.strip('\"')),
                        tokens=include[1:])


def _find_includes(tokens):
    """Find all of the #includes directives in a source file.

    :param list tokens: The list of tokens in the source code.
    :yields list: A list of tokens representing the tokens in an include, e.g.
        ['#include', '<', 'stdio', '.', 'h', '>']. These are returned in the
        same order that they appear in the file.
    """
    for i, token in enumerate(tokens[:-1]):
        if token.value != "#include":
            continue

        if tokens[i + 1].type == "string":
            yield tokens[i:i + 2]
        else:
            angle_include = match_tokens(tokens[i + 1:],
                                         start=match_regex("^<$"),
                                         end=match_regex("^>$"))
            try:
                angle_include = next(angle_include)
            except StopIteration:
                continue

            yield [token] + angle_include
