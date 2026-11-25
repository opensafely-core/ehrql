"""
We support only fixed-length binary types. Python's bytes is variable-length,
so we implement our own type(s) and validate lengths as part of type checking.
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class BaseBinary:
    value: bytes

    def __post_init__(self):
        if len(self.value) != self.length:
            raise ValueError(f"Invalid {self.__class__.__name__}: {self.value}")

    @classmethod
    def _primitive_type(cls):
        return bytes

    # The presence of this method allows query engines to work with values of this type,
    # despite not being explicitly told about them beforehand
    def _to_primitive_type(self):
        return self.value


class BinaryId128(BaseBinary):
    """
    128-bit raw bytes used as an identifier
    """

    length = 16
