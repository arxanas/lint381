"""Install the `lint381` script."""
from setuptools import setup


setup(
    name="lint381",
    version="0.5.2",
    author="Waleed Khan",
    author_email="wkhan@umich.edu",
    description="C and C++ linter for EECS 381.",
    url="https://github.com/arxanas/lint381",

    packages=["lint381"],
    entry_points="""
    [console_scripts]
    lint381=lint381.__main__:main
    """,
    install_requires=["click==6.2"],
)
