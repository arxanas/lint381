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

    for file in files:
        lines = file.read().splitlines()
        errors = linter.lint(lines)

        for line_num, errors in sorted(errors.items()):
            # 1-index the line number.
            line_num = line_num + 1

            for error_message in errors:
                filename = os.path.basename(file.name)
                message = ""
                message += click.style("{}:{}: "
                                       .format(filename, line_num),
                                       bold=True)
                message += click.style("error: ",
                                       fg="red",
                                       bold=True)
                message += error_message
                click.echo(message)
