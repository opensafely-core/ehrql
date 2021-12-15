from typing import Union

from databuilder.functools_utils import singledispatchmethod_with_unions


def test_singledispatchmethod_with_unions():
    class A:
        pass

    class B:
        pass

    class C:
        pass

    class Test:
        @singledispatchmethod_with_unions
        def method(self, value):
            raise TypeError(value)

        @method.register
        def method_a_or_b(self, value: Union[A, B]) -> str:
            return "a_or_b"

        @method.register(C)
        def method_c(self, value):
            return "c"

    test_obj = Test()
    assert test_obj.method(A()) == "a_or_b"
    assert test_obj.method(B()) == "a_or_b"
    assert test_obj.method(C()) == "c"
