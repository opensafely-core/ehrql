from functools import singledispatchmethod
from typing import Union, get_args, get_origin, get_type_hints


class singledispatchmethod_with_unions(singledispatchmethod):
    """
    Workaround for the fact that `singledispatchmethod` can't currently handle Union
    types, see: https://bugs.python.org/issue46014
    """

    def register(self, cls, method=None):
        # If we've been called with a method as a single argument ...
        if method is None and not isinstance(cls, type):
            # (then `cls` is not in fact a class, it's the method)
            target_method = cls
            # ... check if the type of the first argument is a Union ...
            arg_types = get_type_hints(target_method).values()
            first_arg_type = next(iter(arg_types)) if arg_types else None
            if get_origin(first_arg_type) is Union:
                # ... and if so, register the method for each of the types included in
                # the union.
                for type_ in get_args(first_arg_type):
                    super().register(type_, method=target_method)
                return target_method
        return super().register(cls, method=method)


class singledispatch_on_value:
    """
    Like `singledispatch` but dispatches on the *value* of the first argument rather
    than its type
    """

    def __init__(self, default_impl):
        self.default_impl = default_impl
        self.registry = {}

    def register(self, value):
        def wrapper(fn):
            self.registry[value] = fn
            return fn

        return wrapper

    def __call__(self, *args, **kwargs):
        impl = self.registry.get(args[0], self.default_impl)
        return impl(*args, **kwargs)
