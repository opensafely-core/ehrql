from fractions import Fraction
from random import Random

import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from ehrql.dummy_data_nextgen.samplers import Coin, VoseAliasSampler


weightings = st.lists(
    st.fractions(min_value=0) | st.integers(min_value=0), min_size=1
).filter(lambda x: sum(x) > 0)


@example([Fraction(1)])
@example(weights=[1])
@example(weights=[0, 1])
@example(weights=[0, 1, 1]).via("discovered failure")
@given(weightings)
def test_alias_sampler_gives_correct_probabilities(weights):
    total = sum(weights)
    true_probabilities = [Fraction(x) / total for x in weights]

    sampler = VoseAliasSampler(weights)

    calculated_probabilities = [Fraction(0)] * len(weights)

    for i in range(len(weights)):
        p = sampler._probabilities[i]
        assert type(p) is Fraction
        calculated_probabilities[i] += p
        calculated_probabilities[sampler._alias[i]] += 1 - p
    for i in range(len(weights)):
        calculated_probabilities[i] /= len(weights)

    assert true_probabilities == calculated_probabilities


@given(weights=weightings, seed=st.integers(), repetitions=st.integers(0, 100))
@example(
    weights=[1, 2],
    seed=1,
    repetitions=1,
)
@example(
    weights=[1],
    seed=0,
    repetitions=1,
)
@example(weights=[0, 1], seed=1, repetitions=1)
def test_alias_sampler_does_not_sample_zero_weights(weights, seed, repetitions):
    sampler = VoseAliasSampler(weights)
    random = Random(seed)

    for _ in range(repetitions):
        i = sampler.sample(random)
        assert weights[i] > 0


@example(1, 3, Random(0))
@example(1, 2, Random(0))
@settings(report_multiple_bugs=False)
@given(
    st.integers(min_value=0),
    st.integers(min_value=0),
    st.randoms(use_true_random=False),
)
def test_coins_have_right_probability_calculations(m, n, rnd):
    assume(min(m, n) > 0)
    coin = Coin(m, n)

    for _ in range(10):
        coin.toss(rnd)

    desired_p = Fraction(m, n + m)

    p = Fraction(0)

    for i, (a, b) in enumerate(coin.trail):
        if a >= b:
            p += Fraction(1, 2 ** (i + 1))

    remainder = 1 - Fraction(1, 2 ** len(coin.trail))

    assert p <= desired_p <= p + remainder


def test_validates_weights():
    with pytest.raises(ValueError):
        Coin(-1, 1)
    with pytest.raises(ValueError):
        Coin(0, 0)


def test_probability_of_float_coin_is_fraction():
    assert Coin(0.5, 0.5).probability == Fraction(1, 2)
