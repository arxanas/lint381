"""Run the linter on the specified source code files."""
import os.path

import click

from .c import linter as c_linter
from .cpp import linter as cpp_linter


@click.command()
@click.argument("files", nargs=-1, type=click.File())
@click.option("--lang", type=click.Choice(["c", "cpp"]), default="cpp")
def main(files, lang):
    """Lint the files specified on the command-line."""
    linter = {
        "c": c_linter,
        "cpp": cpp_linter,
    }[lang]

    had_errors = False
    for file in files:
        code = file.read().replace("\t", " " * 4)
        errors = linter.lint(code)
        if errors:
            had_errors = True

        for error in errors:
            location = error.tokens[0].start
            filename = os.path.basename(file.name)
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

    if end.row != start.row:
        underline_length = len(line) - start.column
    else:
        underline_length = (end.column - start.column) + 1
    underline_string = "^" * underline_length
    underline_string = (" " * start.column) + underline_string

    click.echo(line)
    click.secho(underline_string, fg="green", bold=True)
