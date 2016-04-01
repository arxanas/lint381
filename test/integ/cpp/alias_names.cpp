using Foo = int;

using bar_t = int;

// Should be accepted because some comparators use this alias name for
// heterogeneous lookup.
using is_transparent = int;
