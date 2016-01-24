typedef struct Foo * Foo_ptr;

typedef struct Foo * Foo_ptr_t;

typedef struct {
    // Should not throw an error.
    struct Foo_t bar;
};
