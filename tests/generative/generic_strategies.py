from hypothesis import strategies as st


# This is a variable that will normally be set to True, but which shrinking is
# allowed to make False.
#
# Examples of where this is useful:
#
# * Turning off expensive test operations that you want to check but don't care
#   about running if they turn out not to be relevant to the error you're
#   seeing.
# * Giving the shrinker a place to terminate generation in places where you've
#   decided to do it yourself because e.g. the data was getting too large.
usually = st.integers(0, 255).map(lambda n: n > 0)


@st.composite
def usually_all_of(draw, options, min_size=1):
    """Generates a list of distinct elements drawn from `options`, of size at least
    `min_size`. In the normal course of things, this will usually be all of `options`,
    but the shrinker is allowed to remove elements from it, which can speed up
    test execution during shrinking significantly."""
    flags = draw(st.lists(usually, min_size=len(options), max_size=len(options)))

    # In order to make sure enough of these are set, we set some
    # of the flags to true. We do this unconditionally on whether enough
    # flags are already set so that when shrinking we don't start to generate
    # more data when some of the flags are shrunk to false.
    extra_flags = draw(
        st.lists(
            st.integers(0, len(options) - 1),
            min_size=min_size,
            max_size=min_size,
            unique=True,
        )
    )
    n_set = flags.count(True)
    for i in extra_flags[: max(min_size - n_set, 0)]:
        flags[i] = True
    return [option for option, include in zip(options, flags) if include]
