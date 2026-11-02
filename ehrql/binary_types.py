# TODO: Write docs for things in this file
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


# TODO: Decide on a better name for this:
# Should "128" (or "16") appear somewhere in the name?
class BinaryIdentifier(BaseBinary):
    """
    128-bit binary used as an identifier
    """

    length = 16
