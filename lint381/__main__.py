"""Run the linter on the specified source code files."""
import click

from .c import linter as c_linter


@click.command()
@click.argument("files", nargs=-1, type=click.File())
def main(files):
    """Lint the files specified on the command-line."""
    for file in files:
        lines = file.read().splitlines()

        if file.name.endswith(".c"):
            errors = c_linter.lint(lines)
        elif file.name.endswith(".cpp"):
            raise NotImplementedError()
        else:
            click.secho("Unknown file type: {}"
                        .format(file.name),
                        fg="red")

        for line_num, errors in sorted(errors.items()):
            # 1-index the line number.
            line_num = line_num + 1

            for error_message in errors:
                message = ""
                message += click.style("{}:{}: "
                                       .format(file.name, line_num),
                                       bold=True)
                message += click.style("error: ",
                                       fg="red",
                                       bold=True)
                message += error_message
                click.echo(message)
