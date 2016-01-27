if (foo == 0) {}
if (foo == '\0') {}
if (foo == NULL) {}
if (foo != 0) {}
if (foo != '\0') {}
if (foo != NULL) {}
if (foo) {}
if (foo == 10) {}

// This is okay and sometimes necessary if the return type won't accept `foo`.
int foo() {
    return bar != NULL;
}

void baz() {}
