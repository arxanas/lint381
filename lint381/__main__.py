"""Run the linter on the specified source code files."""
import os.path

import click

from .c import linter as c_linter


@click.command()
@click.argument("files", nargs=-1, type=click.File())
def main(files):
    """Lint the files specified on the command-line."""
    # TODO: Select at runtime with the --c and --cpp flags.
    linter = c_linter

    had_errors = False
    for file in files:
        code = file.read()
        errors = linter.lint(code)
        if errors:
            had_errors = True

        for error in errors:
            location = error.tokens[0].start

            filename = os.path.basename(file.name)
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

    if had_errors:
        raise SystemExit(1)
