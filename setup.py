"""Install the `lint381` script."""
import os

from setuptools import setup


def get_requirements(requirements_filename):
    """Get the list of requirements from a requirements file.

    :param str requirements_filename: The name of the requirements file, such
        as `requirements.txt`.
    :returns list: A list of dependencies in the requirements file.
    """
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(setup_dir, requirements_filename)
    with open(requirements_path) as f:
        return [i
                for i in f.read().splitlines()
                if i
                if not i.startswith("#")]

setup(
    name="lint381",
    version="0.1.0",
    author="Waleed Khan",
    author_email="wkhan@umich.edu",
    description="C and C++ linter for EECS 381.",
    url="https://github.com/arxanas/lint381",

    packages=["lint381"],
    entry_points="""
    [console_scripts]
    lint381=lint381.__main__:main
    """,
    install_requires=get_requirements("requirements.txt"),
)
