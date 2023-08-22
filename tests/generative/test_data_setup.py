import hypothesis as hyp
from hypothesis.vendor.pretty import pretty

from . import test_query_model


# We just need a single non-empty example to check, and we want to keep the test
# deterministic
@hyp.given(example=test_query_model.data_strategy)
@hyp.settings(max_examples=1, derandomize=True)
def test_data_strategy_examples_round_trip(example):
    """
    Examples produced by `data_strategy` contain references to classes dynamically
    generated in `data_setup` and we need to do some underhand stuff to make sure they
    can be copy/pasted back into `@hypothesis.example()` and evaluate correctly.

    We've broken this properly once without realising so this test ensures we don't do so
    again.
    """
    hyp.assume(len(example) > 0)
    # `pretty` is the formatter Hypothesis uses for examples
    example_repr = pretty(example)
    # Evaluate it in the context of the `test_query_model` module, which is where
    # examples will get pasted
    evaled = eval(example_repr, globals(), vars(test_query_model))
    assert evaled == example
