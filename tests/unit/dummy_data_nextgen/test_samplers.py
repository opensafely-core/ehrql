from collections import Counter
from fractions import Fraction
from random import Random

import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from ehrql.dummy_data_nextgen.samplers import Coin, TreeSampler, VoseAliasSampler


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


@given(
    st.dictionaries(st.text(), st.integers(min_value=0)),
    st.randoms(use_true_random=False),
)
def test_samples_only_non_zero(weights, rnd):
    assume(sum(weights.values()) > 0)
    sampler = TreeSampler(weights)

    assert weights[sampler.sample(rnd)] > 0


@given(
    st.lists(st.tuples(st.integers(0, 5), st.integers(min_value=0))),
    st.randoms(use_true_random=False, note_method_calls=True),
)
def test_samples_only_non_zero_while_updating(weights, rnd):
    sampler = TreeSampler()

    model = {}

    for k, v in weights:
        model[k] = v
        sampler[k] = v
        if v > 0:
            assert sampler[k] == model[k]
        else:
            assert k not in sampler
        if sum(model.values()) > 0:
            s = sampler.sample(rnd)
            assert model[s] > 0


@given(st.randoms(use_true_random=True))
def test_sample_from_single(rnd):
    sampler = TreeSampler()
    sampler[0] = 1
    assert sampler.sample(rnd) == 0


@given(
    st.randoms(use_true_random=False),
    st.data(),
    st.dictionaries(st.text(), st.integers(min_value=1), min_size=2),
)
def test_can_delete_an_item(rnd, data, weights):
    keys = sorted(weights)
    sampler = TreeSampler(weights)
    key = data.draw(st.sampled_from(keys))
    del sampler[key]
    assert sampler.sample(rnd) != key


def test_empty_sample_is_error():
    rnd = Random(0)
    sampler = TreeSampler()
    with pytest.raises(IndexError):
        sampler.sample(rnd)
    sampler[1] = 1
    sampler[1] = 0
    with pytest.raises(IndexError):
        sampler.sample(rnd)


def test_non_empty_sampler_is_truthy():
    sampler = TreeSampler()
    assert not sampler
    sampler[0] = 1
    assert sampler
    del sampler[0]
    assert not sampler


@given(st.dictionaries(st.text(), st.integers(min_value=1)))
def test_iterates_as_dict(weights):
    sampler = TreeSampler(weights)
    assert sorted(sampler) == sorted(weights)
    assert sorted(sampler.items()) == sorted(weights.items())


def test_skips_zero_weights():
    sampler = TreeSampler({1: 1, 2: 0, 3: 1})
    assert sorted(sampler) == [1, 3]


def test_zero_weights_are_absent():
    sampler = TreeSampler()
    sampler[1] = 2
    assert sampler[1] == 2
    sampler[1] = 0
    with pytest.raises(KeyError):
        sampler[1]


def test_items_not_set_are_not_in_sampler():
    sampler = TreeSampler()
    assert 3 not in sampler


def test_heavily_samples_from_biggest_child():
    rnd = Random()
    sampler = TreeSampler()
    for i in range(10):
        sampler[i] = 1

    sampler[10] = 1000

    total = 1000
    count = 0
    for _ in range(total):
        if sampler.sample(rnd) == 10:
            count += 1
    assert count / total >= 0.9


def test_heavily_samples_from_biggest_child_with_floats():
    rnd = Random()
    sampler = TreeSampler()
    for i in range(10):
        sampler[i] = 1.0

    sampler[10] = 1000.0

    total = 1000
    count = 0
    for _ in range(total):
        if sampler.sample(rnd) == 10:
            count += 1
    assert count / total >= 0.9


def test_maintains_distribution_during_deletion():
    counts = {"a": 1000, "b": 5000, "c": 4000}
    values = [k for k, v in counts.items() for _ in range(v)]
    weights = [1.0 / counts[k] for k in values]

    results = Counter()
    sampler = TreeSampler(enumerate(weights))
    random = Random(0)
    for _ in range(1000):
        i = sampler.sample(random)
        sampler[i] = 0
        results[values[i]] += 1
    for s in "abc":
        assert results[s] >= 200
