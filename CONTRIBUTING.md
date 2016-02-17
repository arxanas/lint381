# Getting started

`lint381` is written in Python 3, so to get started, you'll have to have the
relevant developer tools. Install Python 3 on your system, as well as a program
like `virtualenv` to manager your Python environments.

## Check out the repository

Check out the `lint381` repository in a directory. Enter the directory and
create a new `virtualenv`. Make sure to specify Python 3 as the `virtualenv`
executable.

    $ git clone git@github.com:arxanas/lint381
    $ cd lint381
    $ virtualenv -p python3 .venv

Now activate the virtualenv:

    $ source .venv/bin/activate
    (.venv)$

This should succeed, and commands like `which python` should show you the
version of Python installed in `.venv`. When you want to stop using the
`virtualenv`, you can deactivate it so that you can use your regular system
Python:

    (.venv)$ deactivate
    $

> **Note**: You're free to name your `virtualenv` whatever you want, but be aware
> that Pytest may try to run tests that it happens to find in your `virtualenv`
> directory. Some of `lint381`s dependencies have tests bundled with them.

## Install dependencies

Make sure that your `virtualenv` is activated and run the following two
commands to install dependencies:

    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt

Now you can run the test suite:

    $ py.test

The tests should all run and pass. If they don't all pass, you should file an
issue.

On occasion, you may want to run the `lint381` executable by hand. You can
install the `lint381` executable in the virtualenv:

    $ pip install -e .
    $ lint381 test.cpp

# Making changes

Here is how `lint381` works:

  1) Convert each source file into a list of tokens. See `tokenizer.py` for more
information on what a token is.
  2) Run each linting function on each source file's list of tokens. Collect all
the generated linting errors.
  3) Print out all the collected error messages.

You can find the linting functions in `c.py` and `cpp.py`. If you want a
function to apply to both C and C++, write it in `c.py` and modify the list of
imported linters at the top of `cpp.py`.

Each linting function takes a description of the source file as its parameter.
This contains things such as the filename and list of tokens. Usually, we look
at the list of tokens and try to find a subsequence of tokens to flag. See
`linter.py` for a description of what exactly is passed into a linting function.

Manually writing out the same sorts of code to match tokens would be redundant,
so much of it can be done with the helper functions found in `matcher.py`. In
particular, many functions use the `with_matched_tokens` decorator. Consult the
documentation in `matcher.py` for more information.

# Preparing a pull request

Once you've made your changes, make sure that the following hold:

  * You have 100% code coverage. You can test for code coverage by running
    `py.test`; if it shows a percentage less than 100%, then you have not tested
all of your code and need to write test cases. It should tell you which lines of
code have not been tested.
  * You don't have any linter errors (for the Python source code you wrote,
    which is completely unrelated to the `lint381` project itself). Run `flake8
lint381 test` and ensure that it reports no errors.

If these do, you can commit and submit a pull request on Github. Make sure to
reference an issue ID if there is one. Specify what behavior is being
implemented or modified. Once all of the status checks have passed and your code
has been reviewed, it will be merged into master.
