"""C linters."""
from .code import with_matched_tokens
from .linter import Error, Linter

linter = Linter()


@linter.register
@with_matched_tokens(start="^(unsigned|float)$")
def prohibited_types(tokens, *, match):
    """Flag prohibited numeric types."""
    type = match[0]
    typename = type.value
    return Error(message="Prohibited type '{}'"
                         .format(typename),
                 tokens=[type])


@linter.register
@with_matched_tokens(start="^#define$", lookahead=1)
def underscore_define(tokens, *, match):
    """Flag #defines that start with underscores."""
    define = match[1]
    macro = define.value
    if macro.startswith("_"):
        return Error(message="Macro '{}' should not start with an underscore"
                             .format(macro),
                     tokens=[define])


@linter.register
@with_matched_tokens(start="^#define$", lookahead=1)
def uppercase_define(tokens, *, match):
    """Flag non-uppercase #defines."""
    define = match[1]
    macro = define.value
    if not macro.isupper():
        return Error(message="Macro '{}' should be uppercase"
                             .format(macro),
                     tokens=[define])


@linter.register
@with_matched_tokens(start="^(struct|enum|class)$", end="^({|;)$")
def typename_capitalized(tokens, *, match):
    """Flag type names that aren't capitalized."""
    type = match[0].value
    type_name = match[1].value
    if type_name[0].islower():
        return Error(message="{} name '{}' should be capitalized"
                             .format(type.capitalize(), type_name),
                     tokens=[match[1]])


@linter.register
@with_matched_tokens(start="^enum$", end="^{$")
def enums_end_with_e(tokens, *, match):
    """Flag enums that don't end with '_e'."""
    enum = match[1]
    enum_name = enum.value
    if not enum_name.endswith("_e"):
        return Error(message="Enum '{}' should end with '_e'"
                     .format(enum_name),
                     tokens=[enum])


@linter.register
@with_matched_tokens(start="^typedef$", end="^;$")
def typedefs_end_with_t(tokens, *, match):
    """Flag typedefs that don't end with '_t'."""
    typedef = match[-2]
    typedef_name = typedef.value

    # Assume it's a function pointer, so don't try to name that.
    if typedef_name == ")":
        return

    if not typedef_name.endswith("_t"):
        return Error(message="Typedef '{}' should end with '_t'"
                             .format(typedef_name),
                     tokens=[typedef])


@linter.register
@with_matched_tokens(start="^(==|!=)$", end="^\)$")
def comparison_to_zero(tokens, *, match):
    """Flag comparisons to zero or NULL."""
    operator = match[0]
    operand = match[1]

    if operator.value in ["==", "!="] and operand.value in ["0", "NULL"]:
        return Error(message="Comparison to {} should be avoided"
                             .format(operand.value),
                     tokens=[operator, operand])
