# lint381 [![Build Status](https://travis-ci.org/arxanas/lint381.svg?branch=travis-ci)](https://travis-ci.org/arxanas/lint381) [![codecov.io](https://codecov.io/github/arxanas/lint381/coverage.svg?branch=master)](https://codecov.io/github/arxanas/lint381?branch=master)

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
$ lint381 main.c
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
