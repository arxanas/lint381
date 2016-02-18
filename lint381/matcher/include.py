"""Matches includes in a token list."""
import collections
import functools

from . import match_regex, match_tokens


class Include(collections.namedtuple("Include", ["tokens"])):
    """An include appearing in a source file.

    :ivar list tokens: The list of tokens forming the include. For example,
        their values might be ['#include', '<', 'stdio', '.', 'h', '>'].
    """

    @property
    def is_system_include(self):
        """Whether or not the include was for a system header file.

        A system header file is denoted by an angle-bracket include, while a
        user include file is denoted by a quote-include.

        :returns bool:
        """
        # For system includes, the next tokens are '<', 'stdio', '.', 'h', '>'.
        # But for a user include, the next token is a single string token. So
        # we look at the first character of the next token to handle both of
        # these cases.
        return self.tokens[1].value.startswith("<")

    @property
    def include_file(self):
        """The filename being included.

        :returns str:
        """
        if self.is_system_include:
            filename_tokens = self.tokens[2:-1]
            return "".join(token.value for token in filename_tokens)
        else:
            return self.tokens[1].value.strip('"')


def with_includes(func):
    """Decorator for a linter function that automatically finds includes.

    If you need to work with the includes of a source file, you can wrap your
    linter function:

        @linter.register
        @with_includes
        def flag_something(source, *, includes):
            ...

    The value of `includes` is a list of `Include`s in the order that they
    appear in the file.
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        source = args[0]
        includes = list(find_includes(source.tokens))
        kwargs["includes"] = includes
        return func(*args, **kwargs)
    return wrapped


def find_includes(tokens):
    """Find all of the #includes directives in a source file.

    :param list tokens: The list of tokens in the source code.
    :yields Include: The includes in the order that they appear in the file.
    """
    for i, token in enumerate(tokens[:-1]):
        if token.value != "#include":
            continue

        if tokens[i + 1].type == "string":
            yield Include(tokens[i:i + 2])
        else:
            angle_include = match_tokens(tokens[i + 1:],
                                         start=match_regex("^<$"),
                                         end=match_regex("^>$"))
            try:
                angle_include = next(angle_include)
            except StopIteration:
                continue

            yield Include([token] + angle_include)
