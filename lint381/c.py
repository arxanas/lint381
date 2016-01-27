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
@with_matched_tokens(start=match_regex("^(unsigned|float)$"))
def prohibited_types(tokens, *, match):
    """Flag prohibited numeric types."""
    type = match[0]
    typename = type.value
    yield Error(message="Prohibited type '{}'"
                        .format(typename),
                tokens=[type])


@linter.register
@with_matched_tokens(start=match_regex("^#define$"), lookahead=1)
def underscore_define(tokens, *, match):
    """Flag #defines that start with underscores."""
    define = match[1]
    macro = define.value
    if macro.startswith("_"):
        yield Error(message="Macro '{}' should not start with an underscore"
                            .format(macro),
                    tokens=[define])


@linter.register
@with_matched_tokens(start=match_regex("^#define$"), lookahead=1)
def uppercase_define(tokens, *, match):
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
def typename_capitalized(tokens, *, match):
    """Flag type names that aren't capitalized."""
    type = match[0].value
    type_name = match[1].value
    if type_name[0].islower():
        yield Error(message="{} name '{}' should be capitalized"
                            .format(type.capitalize(), type_name),
                    tokens=[match[1]])


@linter.register
@with_matched_tokens(start=match_regex("^enum$"),
                     end=match_type("identifier"))
def enums_end_with_e(tokens, *, match):
    """Flag enums that don't end with '_e'."""
    if len(match) != 2:
        # We picked up an unrelated identifier.
        return

    enum = match[-1]
    enum_name = enum.value
    if not enum_name.endswith("_e"):
        yield Error(message="Enum '{}' should end with '_e'"
                            .format(enum_name),
                    tokens=[enum])


@linter.register
@with_matched_tokens(start=match_regex("^typedef$"),
                     end=match_regex("^;$"))
def typedefs_end_with_t(tokens, *, match):
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
def comparison_to_null(tokens, *, match):
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
def enum_members_all_caps(tokens, *, match):
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
def cast_malloc(tokens, *, match):
    """Flag casting the result of 'malloc'."""
    # Ensure that the open paren matches with a close paren right before the
    # malloc (i.e. is a cast).
    close_paren = match[-2]
    if close_paren.value != ")":
        return

    yield Error(message="Don't cast the result of malloc",
                tokens=match[:-1])
