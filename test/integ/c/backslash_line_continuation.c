// Regression test: ensure that we don't fail to parse a backslash at the end
// of a line.

#define FUNC(foo) foo; \
    foo;
