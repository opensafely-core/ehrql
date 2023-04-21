import dataclasses

import pytest

from ehrql.utils.functools_utils import (
    cached_method,
    singledispatchmethod_with_cache,
)


@pytest.fixture
def TestClass():
    COUNTER = 0

    class TestClass:
        @singledispatchmethod_with_cache
        def test(self, value):
            assert False

        @test.register(str)
        def test_str(self, value):
            # Use a shared counter to give different results for each call
            nonlocal COUNTER
            COUNTER += 1
            return value, COUNTER

    return TestClass


def test_results_are_cached(TestClass):
    obj = TestClass()
    assert obj.test("hello") is obj.test("hello")


def test_cache_is_unique_to_instances(TestClass):
    obj1 = TestClass()
    obj2 = TestClass()
    assert obj1.test("hello") is not obj2.test("hello")


def test_cache_can_be_cleared(TestClass):
    obj = TestClass()
    result = obj.test("hello")
    obj.test.cache_clear()
    assert result is not obj.test("hello")


def test_clearing_cache_only_affects_single_instance(TestClass):
    obj1 = TestClass()
    obj2 = TestClass()
    result1 = obj1.test("hello")
    result2 = obj2.test("hello")
    obj1.test.cache_clear()
    assert result1 is not obj1.test("hello")
    assert result2 is obj2.test("hello")


def test_cached_method():
    CALL_COUNT = 0

    @dataclasses.dataclass(frozen=True)
    class SomeValue:
        n: int

        @cached_method
        def n_plus_one(self):
            nonlocal CALL_COUNT
            CALL_COUNT += 1
            return self.n + 1

    value = SomeValue(42)
    assert CALL_COUNT == 0
    assert value.n_plus_one() == 43
    assert CALL_COUNT == 1
    assert value.n_plus_one() == 43
    assert CALL_COUNT == 1
