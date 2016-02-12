# lint381 [![Build Status](https://travis-ci.org/arxanas/lint381.svg?branch=travis-ci)](https://travis-ci.org/arxanas/lint381) [![codecov.io](https://codecov.io/github/arxanas/lint381/coverage.svg?branch=master)](https://codecov.io/github/arxanas/lint381?branch=master) [![PyPI version](https://img.shields.io/pypi/v/lint381.svg)](https://pypi.python.org/pypi/lint381)

`lint381` checks your EECS 381 projects for coding style errors.

See http://umich.edu/~eecs381/ for the course homepage. The coding standards
can be found here:

  * [C coding standard](http://umich.edu/~eecs381/handouts/C_Coding_Standards.pdf)
  * [C++ coding standard](http://umich.edu/~eecs381/handouts/C++_Coding_Standards.pdf)

# Usage

`lint381` requires Python 3. Install with `pip install lint381`. Then run it on
your source files:

```
$ cat main.c
enum foo {
    bar,
    baz
}
$ lint381 --lang=c main.c
main.c:1:6: error: Enum name 'foo' should be capitalized
enum foo {
     ^^^
main.c:1:6: error: Enum 'foo' should end with '_e'
enum foo {
     ^^^
main.c:2:5: error: Enum member 'bar' should be all-caps
    bar,
    ^^^
main.c:3:5: error: Enum member 'baz' should be all-caps
    baz
    ^^^
```

You can use `--lang=c` or `--lang=cpp` to check your code in different modes.
The default is C++.

# Features

## C checks

The C linter flags the following:

  * Use of prohibited types (such as `unsigned` and `float`).
  * Macros that start with an underscore, as they are reserved by the
	implementation.
  * Non-uppercase `#defines` (`#define foo` is wrong, `#define FOO` is right).
  * `struct`s and `enum`s that aren't capitalized.
  * `enum`s that don't end with `_e`.
  * `typedef`s that don't end with `_t`.
  * Non-idiomatic comparison to `NULL` (such as `if (foo == NULL)`).
  * Enum members that aren't all-caps.
  * Casting the result of `malloc` (such as `foo = (char*) malloc(...)`).

## C++ checks

The C++ linter flags the following:

  * All C checks above, except those that are obviated (e.g. we now use
	`nullptr` instead of `NULL`, and don't use `malloc`).
  * Comments with three asterisks (`***`) as those are provided by Kieras and
	should be removed.
  * Use of `NULL` instead of `nullptr`.
  * Use of `malloc`/`free` instead of `new`/`delete`.
  * Use of `typedef` instead of `using`.
