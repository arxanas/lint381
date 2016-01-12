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
#define __FOO__

int main() {
    // ...
}
$ lint381 main.c
main.c:1: error: Macro '__FOO__' should not start with an underscore
```
