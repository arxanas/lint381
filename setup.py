"""Install the `lint381` script."""
from setuptools import find_packages, setup


setup(
    name="lint381",
    version="1.3.9",
    author="Waleed Khan",
    author_email="wkhan@umich.edu",
    description="C and C++ linter for EECS 381.",
    url="https://github.com/arxanas/lint381",

    packages=find_packages(),
    entry_points="""
    [console_scripts]
    lint381=lint381.__main__:main
    """,
    install_requires=["click==6.2"],
)
