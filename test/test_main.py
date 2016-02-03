"""Test the main executable."""
import os.path

from click.testing import CliRunner
import pytest

from lint381.__main__ import main


def source_code_files(language):
    """Get the source code files of the specified language.

    :param str language: One of "c" or "cpp".
    :returns list: A list of source code filenames.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    integ_test_dir = os.path.join(script_dir, "integ", language)

    tests = []
    for i in os.listdir(integ_test_dir):
        if not i.endswith(".{}".format(language)):
            continue

        input_filename = os.path.join(integ_test_dir, i)
        output_filename = input_filename + ".out"
        tests.append((
            language,
            input_filename,
            output_filename,
        ))
    return tests


@pytest.mark.parametrize("language, input, output",
                         source_code_files("c") + source_code_files("cpp"))
def test_integ(language, input, output):
    """Run integration tests."""
    runner = CliRunner()
    result = runner.invoke(main, ["--lang", language, input])
    with open(output) as f:
        expected_output = f.read()
        assert result.output == expected_output
        if expected_output:
            assert result.exit_code != 0
        else:
            assert result.exit_code == 0
