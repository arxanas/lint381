"""Run the linter on the specified source code files."""
import os.path

import click

from .c import linter as c_linter
from .cpp import linter as cpp_linter


_LINTERS = {
    "c": c_linter,
    "cpp": cpp_linter,
}
"""A map of language to linter."""


@click.command()
@click.argument("files", nargs=-1, type=click.File())
@click.option("--lang", type=click.Choice(_LINTERS.keys()), default="cpp")
def main(files, lang):
    """Lint the files specified on the command-line."""
    linter = _LINTERS[lang]

    had_errors = False
    for file in files:
        # The tokenizer doesn't handle tabs, so don't pass any in.
        code = file.read().replace("\t", " " * 4)

        filename = os.path.basename(file.name)
        errors = linter.lint(filename, code)
        if errors:
            had_errors = True

        for error in errors:
            location = error.tokens[0].start
            _print_error(error, filename, location)
            _print_tokens(error, code)

    if had_errors:
        raise SystemExit(1)


def _print_error(error, filename, location):
    """Print the error message."""
    message = ""
    message += click.style("{filename}:{row}:{column}: "
                           .format(filename=filename,
                                   row=location.row + 1,
                                   column=location.column + 1),
                           bold=True)
    message += click.style("error: ",
                           fg="red",
                           bold=True)
    message += error.message
    click.echo(message)


def _print_tokens(error, code):
    """Print out and underline the afflicted tokens in the error."""
    start = error.tokens[0].start
    end = error.tokens[-1].end

    lines = code.splitlines()
    line = lines[start.row]

    if start.row == end.row:
        underline_length = (end.column - start.column) + 1
    else:
        # It's possible for an error to span more than one line. The simplest
        # example is a multi-line comment. In that case, only underline tokens
        # on the first line.
        underline_length = len(line) - start.column
    underline_string = "^" * underline_length
    underline_string = (" " * start.column) + underline_string

    click.echo(line)
    click.secho(underline_string, fg="green", bold=True)
